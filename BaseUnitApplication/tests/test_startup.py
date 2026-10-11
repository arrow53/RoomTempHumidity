"""Regression coverage for a missing Thread address during desktop startup."""
import asyncio
import http.client
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from room_monitor import __main__ as app
from room_monitor.storage import Store
from tests.test_collector import payload


@unittest.skipUnless(importlib.util.find_spec("aiocoap"), "install requirements.txt for receiver startup tests")
class StartupTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        root = Path(self.temp.name)
        rooms = {"0123456789abcdef": "Room"}
        (root / "rooms.json").write_text(json.dumps(rooms))
        self.db = root / "live.sqlite3"
        store = Store(self.db, "live", rooms)
        store.ingest(payload())
        store.close()
        self.args = app.parser().parse_args([
            "--db", str(self.db), "--rooms", str(root / "rooms.json"),
            "--http-port", "0", "--coap-host", "::1"])
        self.server = None
        self.task = None
        self.context = AsyncMock()

    async def asyncTearDown(self):
        if self.task:
            self.task.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await self.task
        self.temp.cleanup()

    def get(self, path):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=2)
        try:
            connection.request("GET", path)
            response = connection.getresponse()
            self.assertEqual(response.status, 200)
            return json.loads(response.read())
        finally:
            connection.close()

    async def exercise(self, recover):
        from aiocoap.error import ResolutionError
        missing = asyncio.Event()
        ready = asyncio.Event()
        attempts = 0

        async def bind(store, host, port):
            nonlocal attempts
            attempts += 1
            self.assertEqual((host, port), ("::1", 5683))
            if attempts == 1:
                raise OSError("address not available")
            if not ready.is_set():
                missing.set()
                raise ResolutionError("Thread address missing")
            return self.context

        original_make_server = app.make_server

        def capture_server(*args, **kwargs):
            self.server = original_make_server(*args, **kwargs)
            return self.server

        with patch.object(app, "COAP_RETRY_SECONDS", 0.01), \
             patch.object(app, "make_server", capture_server), \
             patch("room_monitor.coap_server.create_context", side_effect=bind):
            self.task = asyncio.create_task(app.run(self.args))
            await asyncio.wait_for(missing.wait(), 2)
            health = await asyncio.to_thread(self.get, "/healthz")
            self.assertEqual(health["receiver"]["state"], "waiting")
            status = await asyncio.to_thread(self.get, "/api/status")
            self.assertEqual(status["rooms"][0]["temperature_c"], 21.5)
            if recover:
                ready.set()
                async with asyncio.timeout(2):
                    while (await asyncio.to_thread(self.get, "/healthz"))["receiver"]["state"] != "listening":
                        await asyncio.sleep(0.01)
            self.task.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await self.task
            self.task = None
            self.assertEqual(self.context.shutdown.await_count, int(recover))
            self.assertEqual(self.server.socket.fileno(), -1)

    async def test_dashboard_available_during_missing_address_then_receiver_recovers(self):
        await self.exercise(recover=True)

    async def test_shutdown_while_waiting_releases_http_listener(self):
        await self.exercise(recover=False)

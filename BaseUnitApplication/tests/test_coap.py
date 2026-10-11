"""Real IPv6 UDP integration tests, optional when aiocoap isn't installed."""
import asyncio
import importlib.util
import json
import socket
import sys
import tempfile
import unittest
from pathlib import Path

from room_monitor.storage import Store
from tests.test_collector import payload


@unittest.skipUnless(importlib.util.find_spec("aiocoap"), "install requirements.txt for real CoAP integration")
class CoAPTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        import aiocoap
        from room_monitor.coap_server import create_context
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.store = Store(Path(self.temp.name)/"live.db", "live", {"0123456789abcdef":"Room"})
        with socket.socket(socket.AF_INET6, socket.SOCK_DGRAM) as sock:
            sock.bind(("::1", 0))
            self.port = sock.getsockname()[1]
        self.server = await create_context(self.store, "::1", self.port)
        self.client = await aiocoap.Context.create_client_context(transports=["simple6"] if sys.platform == "win32" else ["udp6"])

    async def asyncTearDown(self):
        await self.client.shutdown()
        await self.server.shutdown()
        self.store.close()
        self.temp.cleanup()

    async def send(self, body, content_format=50, path="readings"):
        import aiocoap
        request = aiocoap.Message(code=aiocoap.POST, uri=f"coap://[::1]:{self.port}/{path}", payload=body, content_format=content_format)
        return await asyncio.wait_for(self.client.request(request).response, timeout=5)

    async def test_real_udp_delivery_and_duplicate(self):
        import aiocoap
        first = await self.send(payload())
        self.assertEqual(first.code, aiocoap.CHANGED)
        self.assertEqual(json.loads(first.payload)["status"], "stored")
        second = await self.send(payload())
        self.assertEqual(json.loads(second.payload)["status"], "duplicate")
        self.assertEqual(self.store.summary()["rooms"][0]["temperature_c"], 21.5)

    async def test_coap_error_codes(self):
        import aiocoap
        self.assertEqual((await self.send(payload(), 0)).code, aiocoap.UNSUPPORTED_CONTENT_FORMAT)
        self.assertEqual((await self.send(b"{}" )).code, aiocoap.BAD_REQUEST)
        self.assertEqual((await self.send(payload(node_id="ffffffffffffffff"))).code, aiocoap.FORBIDDEN)
        self.assertEqual((await self.send(payload(), path="missing")).code, aiocoap.NOT_FOUND)
        await self.send(payload())
        self.assertEqual((await self.send(payload(sequence=0, uptime_s=0))).code, aiocoap.CONFLICT)

    async def test_normal_reboot_over_udp(self):
        import aiocoap
        await self.send(payload(sequence=900, uptime_s=90000))
        self.assertEqual((await self.send(payload(boot_id="b"*32, sequence=0, uptime_s=0))).code, aiocoap.CHANGED)
        self.assertEqual((await self.send(payload(sequence=901, uptime_s=90060))).code, aiocoap.CONFLICT)


if __name__ == "__main__":
    unittest.main()

import concurrent.futures
import http.client
import json
import tempfile
import threading
import unittest
from pathlib import Path

from room_monitor import demo
from room_monitor.http_server import make_server
from room_monitor.protocol import ReadingError, parse_reading
from room_monitor.storage import Store, load_rooms


def payload(**changes):
    packet = dict(schema_version=1, node_id="0123456789abcdef", sequence=1, uptime_s=60,
                  boot_id="0123456789abcdef0123456789abcdef",
                  temperature_c=21.5, humidity_pct=45.0)
    packet.update(changes)
    return json.dumps(packet).encode()


class ProtocolTests(unittest.TestCase):
    def test_round_trip_and_boundaries(self):
        for temperature, humidity in [(-40, 0), (125, 100)]:
            self.assertEqual(parse_reading(payload(temperature_c=temperature, humidity_pct=humidity))["temperature_c"], temperature)
        self.assertEqual(parse_reading(payload(sequence=9007199254740991, uptime_s=9007199254740991))["sequence"], 9007199254740991)

    def test_invalid_fields(self):
        cases = [dict(schema_version=True), dict(schema_version=2), dict(node_id="<script>"),
                 dict(node_id="x"*65), dict(boot_id="a"*31), dict(boot_id="A"*32), dict(boot_id=5),
                 dict(sequence=-1), dict(sequence=2**53), dict(sequence=True),
                 dict(sequence=1.5), dict(uptime_s=-1), dict(temperature_c="21"),
                 dict(temperature_c=126), dict(temperature_c=-41), dict(humidity_pct=101),
                 dict(humidity_pct=-1), dict(humidity_pct=False), dict(temperature_c=float("nan")),
                 dict(temperature_c=float("inf")), dict(extra=1)]
        for fields in cases:
            with self.subTest(fields=fields), self.assertRaises(ReadingError):
                parse_reading(payload(**fields))

    def test_malformed_json(self):
        for value in [b"{}", b"[]", b"null", b"\xff", b"{" , b" " * 1025,
                      payload().replace(b'"schema_version": 1', b'"schema_version": 1, "schema_version": 1')]:
            with self.subTest(value=value[:80]), self.assertRaises(ReadingError):
                parse_reading(value)


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.path = Path(self.temp.name) / "test.sqlite3"
        self.now = 2000000000.0
        self.rooms = {"0123456789abcdef": "Living room", "fedcba9876543210": "Bedroom"}
        self.store = Store(self.path, "live", self.rooms, clock=lambda: self.now, max_rows=10)

    def tearDown(self):
        self.store.close()
        self.temp.cleanup()

    def test_waiting_fresh_stale_offline(self):
        self.assertEqual(self.store.summary()["rooms"][0]["status"], "waiting")
        self.store.ingest(payload())
        self.assertEqual(self.store.summary()["rooms"][0]["status"], "fresh")
        self.now += 181
        self.assertEqual(self.store.summary()["rooms"][0]["status"], "stale")
        self.now += 420
        self.assertEqual(self.store.summary()["rooms"][0]["status"], "offline")

    def test_duplicate_does_not_refresh_or_insert(self):
        first = self.store.ingest(payload())
        self.now += 700
        duplicate = self.store.ingest(payload())
        self.assertEqual(duplicate["status"], "duplicate")
        self.assertEqual(first["received_at"], duplicate["received_at"])
        self.assertEqual(self.store.summary()["rooms"][0]["status"], "offline")
        self.assertEqual(self.store.db.execute("SELECT count(*) FROM readings").fetchone()[0], 1)

    def test_reordering_reboot_conflict_and_unknown_node(self):
        self.store.ingest(payload(sequence=8, uptime_s=100))
        for changes in [dict(sequence=7, uptime_s=101), dict(sequence=8, temperature_c=30),
                        dict(sequence=9, uptime_s=99), dict(sequence=0, uptime_s=0), dict(node_id="ffffffffffffffff")]:
            with self.subTest(changes=changes), self.assertRaises(ReadingError):
                self.store.ingest(payload(**changes))

    def test_state_persists_across_collector_restart(self):
        self.store.ingest(payload())
        self.store.close()
        self.store = Store(self.path, "live", self.rooms, clock=lambda:self.now)
        self.assertEqual(self.store.ingest(payload())["status"], "duplicate")
        with self.assertRaises(ReadingError): self.store.ingest(payload(sequence=0, uptime_s=0))

    def test_explicit_reset_retains_history(self):
        self.store.ingest(payload(sequence=100, uptime_s=8000))
        self.store.reset_node("0123456789abcdef")
        self.now += 1
        self.store.ingest(payload(sequence=0, uptime_s=0))
        self.assertEqual(self.store.db.execute("SELECT count(*) FROM readings").fetchone()[0], 2)

    def test_normal_reboot_and_retired_boot_replay(self):
        self.store.ingest(payload(sequence=4000, uptime_s=90000))
        self.now += 1
        reboot = payload(boot_id="1"*32, sequence=0, uptime_s=0)
        self.assertEqual(self.store.ingest(reboot)["status"], "stored")
        self.assertEqual(self.store.ingest(reboot)["status"], "duplicate")
        with self.assertRaises(ReadingError): self.store.ingest(payload(sequence=4001, uptime_s=90001))
        self.store.close()
        self.store = Store(self.path, "live", self.rooms, clock=lambda:self.now)
        with self.assertRaises(ReadingError): self.store.ingest(payload(sequence=4002, uptime_s=90002))
        self.assertEqual(self.store.ingest(payload(boot_id="1"*32, sequence=1, uptime_s=60))["status"], "stored")

    def test_boot_ledger_remains_bounded_without_eviction(self):
        self.store.max_boots = 2
        self.store.ingest(payload())
        self.store.ingest(payload(boot_id="1"*32, sequence=0, uptime_s=0))
        with self.assertRaisesRegex(ReadingError, "ledger full"):
            self.store.ingest(payload(boot_id="2"*32, sequence=0, uptime_s=0))
        with self.assertRaises(ReadingError): self.store.ingest(payload(sequence=2, uptime_s=61))
        self.assertEqual(self.store.db.execute("SELECT count(*) FROM boots").fetchone()[0], 2)
        self.assertEqual(self.store.ingest(payload(boot_id="1"*32, sequence=1, uptime_s=60))["status"], "stored")

    def test_shared_firmware_vectors(self):
        vectors = json.loads((Path(__file__).parents[1]/"protocol/reboot-replay-vectors.json").read_text())["events"]
        for event in vectors:
            with self.subTest(label=event["label"]):
                body = json.dumps(event["reading"]).encode()
                if event["expected"] == "reject_conflict":
                    with self.assertRaises(ReadingError): self.store.ingest(body)
                else:
                    expected = "stored" if event["expected"] == "accept" else "duplicate"
                    self.assertEqual(self.store.ingest(body)["status"], expected)
                    if event["label"] == "old_boot_replay":
                        self.assertEqual(self.store.summary()["rooms"][0]["temperature_c"], 21.4)
                self.now += 1

    def test_retired_latest_retry_after_sample_retention(self):
        first = self.store.ingest(payload())
        self.store.ingest(payload(boot_id="1"*32, sequence=0, uptime_s=0))
        self.now += 31*86400
        self.store.prune()
        result = self.store.ingest(payload())
        self.assertEqual(result, {"status":"duplicate", "received_at":first["received_at"]})
        self.assertEqual(self.store.summary()["rooms"][0]["status"], "waiting")

    def test_retention_row_limit_and_replay_state(self):
        for i in range(30):
            self.store.ingest(payload(sequence=i, uptime_s=i), received_at=self.now+i)
        self.now += 30
        self.assertEqual(self.store.db.execute("SELECT count(*) FROM readings").fetchone()[0], 10)
        self.now += 31*86400
        self.store.prune()
        self.assertEqual(self.store.db.execute("SELECT count(*) FROM readings").fetchone()[0], 0)
        with self.assertRaises(ReadingError): self.store.ingest(payload(sequence=0, uptime_s=0))

    def test_history_is_bounded_and_isolates_nodes(self):
        for i in range(10): self.store.ingest(payload(sequence=i, uptime_s=i), received_at=self.now-100+i*10)
        self.store.ingest(payload(node_id="fedcba9876543210", temperature_c=99))
        result = self.store.history("0123456789abcdef", hours=1, limit=3)
        self.assertLessEqual(len(result["points"]), 3)
        self.assertEqual(sum(row["samples"] for row in result["points"]), 10)
        self.assertTrue(all(row["temperature_c"] == 21.5 for row in result["points"]))
        for kwargs in [dict(hours=float("nan")), dict(hours=-1), dict(limit=1001), dict(hours=9999)]:
            with self.assertRaises(ValueError): self.store.history("0123456789abcdef", **kwargs)

    def test_mode_separation(self):
        with self.assertRaises(ValueError): Store(self.path, "demo", demo.ROOMS)
        with self.assertRaises(ValueError): demo.seed(self.store)
        with self.assertRaises(ValueError): Store(Path(self.temp.name)/"other.db", "live", {"demo-living":"Room"})

    def test_concurrent_duplicate_delivery(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            results = list(executor.map(lambda _:self.store.ingest(payload()), range(20)))
        self.assertEqual(sum(r["status"] == "stored" for r in results), 1)

    def test_collector_clock_rollback(self):
        self.store.ingest(payload())
        self.now -= 60
        self.assertEqual(self.store.summary()["rooms"][0]["status"], "clock_error")
        with self.assertRaises(ReadingError): self.store.ingest(payload(sequence=2, uptime_s=61))

    def test_removed_node_data_deleted_on_config_reload(self):
        self.store.ingest(payload(node_id="fedcba9876543210"))
        self.store.close()
        self.store = Store(self.path, "live", {"0123456789abcdef":"Renamed"}, clock=lambda:self.now)
        self.assertEqual(self.store.db.execute("SELECT count(*) FROM readings").fetchone()[0], 0)


class HTTPTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.store = Store(Path(self.temp.name)/"test.db", "live", {"0123456789abcdef":"Living room"})
        self.server = make_server(self.store, port=0)
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown(); self.thread.join(); self.server.server_close()
        self.store.close(); self.temp.cleanup()

    def request(self, path, method="GET", headers=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        connection.request(method, path, headers=headers or {})
        response = connection.getresponse()
        result = response.status, dict(response.getheaders()), response.read()
        connection.close()
        return result

    def test_static_api_and_path_traversal(self):
        self.assertEqual(self.request("/")[0], 200)
        self.assertEqual(self.request("/app.js")[0], 200)
        code, headers, body = self.request("/api/status")
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(body)["rooms"][0]["status"], "waiting")
        self.assertIn("Content-Security-Policy", headers)
        self.assertEqual(self.request("/../config/rooms.json")[0], 404)
        self.assertEqual(self.request("/api/history?node_id=unknown")[0], 400)
        self.assertEqual(self.request("/api/history?node_id=0123456789abcdef&hours=nan")[0], 400)

    def test_read_only_loopback_and_host_checks(self):
        self.assertEqual(self.request("/api/status", method="POST")[0], 501)
        self.assertEqual(self.request("/", headers={"Host":"evil.example"})[0], 403)
        self.assertEqual(self.request("/api/status", headers={"Sec-Fetch-Site":"cross-site"})[0], 403)
        with self.assertRaises(ValueError): make_server(self.store, "0.0.0.0")


class ConfigTests(unittest.TestCase):
    def test_config_validation(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as folder:
            path = Path(folder)/"rooms.json"
            for contents in [[], {"x":""}, {"x":"a"*61}, {"<x>":"Room"}]:
                path.write_text(json.dumps(contents))
                with self.assertRaises(ValueError): load_rooms(path)
            path.write_text('{"0123456789abcdef":" Study "}')
            self.assertEqual(load_rooms(path), {"0123456789abcdef":"Study"})


if __name__ == "__main__":
    unittest.main()

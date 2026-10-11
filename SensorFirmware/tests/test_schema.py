import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from validate_payload import load_payload, validate


class SchemaTests(unittest.TestCase):
    def setUp(self):
        self.example = json.loads((ROOT / "protocol/example-reading.json").read_text())

    def rejects(self, key, *values):
        for value in values:
            with self.subTest(key=key, value=value):
                payload = copy.deepcopy(self.example)
                payload[key] = value
                with self.assertRaises(ValueError):
                    validate(payload)

    def test_example(self):
        validate(self.example)

    def test_required_fields(self):
        for key in self.example:
            p = dict(self.example)
            del p[key]
            with self.assertRaises(ValueError):
                validate(p)

    def test_collector_owned_fields_not_in_payload(self):
        self.rejects("received_at", "2026-10-10T00:00:00Z")
        self.rejects("room", "Kitchen")

    def test_identity(self):
        self.rejects("node_id", "", "0123456789abcde", "0123456789abcdef0", "0123456789ABCDEF", "node-01", None)

    def test_boot_identity(self):
        self.rejects("boot_id", "", "a" * 31, "a" * 33, "A" * 32, "g" * 32, None, 0)
        for value in ("0" * 32, "f" * 32):
            validate(dict(self.example, boot_id=value))

    def test_reboot_and_replay_contract_vectors(self):
        # Verify fixture identities/body relationships; this does not execute
        # the sibling collector. That task must run these events against storage.
        vectors = json.loads((ROOT / "protocol/reboot-replay-vectors.json").read_text())
        events = {event["label"]: validate(event["reading"]) for event in vectors["events"]}
        key = lambda p: (p["node_id"], p["boot_id"], p["sequence"])
        old, new = events["old_boot"], events["new_boot_reset"]
        self.assertEqual(old["node_id"], new["node_id"])
        self.assertNotEqual(old["boot_id"], new["boot_id"])
        self.assertLess(new["sequence"], old["sequence"])
        self.assertLess(new["uptime_s"], old["uptime_s"])
        self.assertNotEqual(key(old), key(new))
        self.assertEqual(old, events["identical_retry"])
        self.assertEqual(old, events["old_boot_replay"])
        self.assertEqual(key(new), key(events["conflicting_retry"]))
        self.assertNotEqual(new, events["conflicting_retry"])

    def test_version(self):
        self.rejects("schema_version", 0, 2, "1", True, None)

    def test_sequence_and_uptime(self):
        for key in ("sequence", "uptime_s"):
            self.rejects(key, -1, 9007199254740992, 1.5, "1", True, None)
            for value in (0, 1024, 9007199254740991):
                validate(dict(self.example, **{key: value}))

    def test_temperature(self):
        self.rejects("temperature_c", -40.001, 125.001, float("nan"), float("inf"), "21", None, True)
        for value in (-40, -0.001, 0, 125):
            validate(dict(self.example, temperature_c=value))

    def test_humidity(self):
        self.rejects("humidity_pct", -0.001, 100.001, float("nan"), float("inf"), "50", None, True)
        for value in (0, 0.001, 100):
            validate(dict(self.example, humidity_pct=value))

    def test_duplicate_json_keys(self):
        text = json.dumps(self.example).replace('"schema_version": 1', '"schema_version": 1, "schema_version": 1')
        with self.assertRaises(ValueError):
            load_payload(text)

    def test_unknown_schema_rule_fails_closed(self):
        with self.assertRaises(ValueError):
            validate(1, {"multipleOf": 2})


if __name__ == "__main__":
    unittest.main()

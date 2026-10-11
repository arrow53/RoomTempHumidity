"""Wire schema v1. No sensor wall clock is required."""
import hashlib
import json
import math
import re

MAX_PAYLOAD = 1024
FIELDS = {"schema_version", "node_id", "boot_id", "sequence", "uptime_s", "temperature_c", "humidity_pct"}
NODE_ID = re.compile(r"[0-9a-f]{16}\Z")


class ReadingError(ValueError):
    def __init__(self, message, kind="invalid"):
        super().__init__(message)
        self.kind = kind


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ReadingError("duplicate JSON key")
        result[key] = value
    return result


def parse_reading(payload):
    if len(payload) > MAX_PAYLOAD:
        raise ReadingError("payload exceeds 1024 bytes", "too_large")
    try:
        data = json.loads(payload.decode("utf-8"), object_pairs_hook=_unique,
                          parse_constant=lambda _: (_ for _ in ()).throw(ReadingError("non-finite number")))
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ReadingError("invalid UTF-8 JSON") from exc
    if not isinstance(data, dict) or set(data) != FIELDS:
        raise ReadingError("expected exactly the seven schema v1 fields")
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise ReadingError("unsupported schema_version")
    if not isinstance(data["node_id"], str) or not NODE_ID.fullmatch(data["node_id"]):
        raise ReadingError("node_id must be 16 lowercase hex characters")
    if not isinstance(data["boot_id"], str) or not re.fullmatch(r"[0-9a-f]{32}", data["boot_id"]):
        raise ReadingError("boot_id must be 16 random bytes encoded as 32 lowercase hex characters")
    for key in ("sequence", "uptime_s"):
        if type(data[key]) is not int or not 0 <= data[key] <= 9007199254740991:
            raise ReadingError(key + " must be an integer from 0 to 9007199254740991")
    for key, low, high in (("temperature_c", -40, 125), ("humidity_pct", 0, 100)):
        value = data[key]
        if type(value) not in (int, float) or not math.isfinite(value) or not low <= value <= high:
            raise ReadingError(f"{key} must be finite and between {low} and {high}")
        data[key] = float(value)
    return data


def fingerprint(reading):
    return hashlib.sha256(json.dumps(reading, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

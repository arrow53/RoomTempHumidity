"""Small dependency-free validator for exactly this project's schema vocabulary.

This is a test/collector-contract utility, not a general JSON Schema engine.
Unknown schema keywords are rejected to prevent silently skipped constraints.
"""
import json
import math
import re
from pathlib import Path

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "protocol/readings-v1.schema.json"


def validate(value, schema=None):
    if schema is None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    known = {"$schema", "title", "description", "type", "additionalProperties",
             "required", "properties", "const", "pattern", "minimum", "maximum"}
    if set(schema) - known:
        raise ValueError("Unsupported schema vocabulary")
    kind = schema.get("type")
    valid_type = {
        "object": isinstance(value, dict),
        "string": isinstance(value, str),
        "integer": type(value) is int,
        "number": type(value) in (int, float),
        None: True,
    }
    if kind not in valid_type or not valid_type[kind]:
        raise ValueError(f"Expected {kind}")
    if "const" in schema and (type(value) is not type(schema["const"]) or value != schema["const"]):
        raise ValueError("Incorrect constant")
    if type(value) in (int, float):
        if not math.isfinite(value):
            raise ValueError("Non-finite number")
        if "minimum" in schema and value < schema["minimum"]:
            raise ValueError("Below minimum")
        if "maximum" in schema and value > schema["maximum"]:
            raise ValueError("Above maximum")
    if "pattern" in schema and re.fullmatch(schema["pattern"], value) is None:
        raise ValueError("Incorrect string pattern")
    if kind == "object":
        if set(schema.get("required", [])) - value.keys():
            raise ValueError("Missing required property")
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False and value.keys() - props.keys():
            raise ValueError("Unknown property")
        for key in value.keys() & props.keys():
            validate(value[key], props[key])
    return value


def load_payload(text):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("Duplicate property")
            result[key] = value
        return result
    return validate(json.loads(text, object_pairs_hook=pairs))


if __name__ == "__main__":
    import sys
    for filename in sys.argv[1:]:
        load_payload(Path(filename).read_text(encoding="utf-8"))
        print(f"VALID: {filename}")

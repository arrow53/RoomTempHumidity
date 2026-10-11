"""Deterministic, visibly simulated room data. Never starts a live receiver."""
import json
import math
import secrets

ROOMS = {"d000000000000001": "Living room", "d000000000000002": "Bedroom", "d000000000000003": "Office", "d000000000000004": "Kitchen"}
BOOT_IDS = {node: secrets.token_hex(16) for node in ROOMS}


def packet(node, sequence, timestamp):
    index = list(ROOMS).index(node)
    wave = math.sin(timestamp / 1800 + index)
    return json.dumps({"schema_version": 1, "node_id": node, "sequence": sequence,
                       "boot_id": BOOT_IDS[node],
                       "uptime_s": sequence * 60, "temperature_c": round([21.6, 19.2, 22.4, 21.1][index] + wave * .6, 2),
                       "humidity_pct": round([45, 49, 42, 54][index] + math.cos(timestamp / 2600 + index) * 3, 1)}).encode()


def seed(store):
    now = store.clock()
    # Clear only the demo database, which Store has already verified by metadata.
    if store.mode != "demo":
        raise ValueError("cannot seed a live database")
    with store.lock, store.db:
        store.db.execute("DELETE FROM readings")
        store.db.execute("DELETE FROM node_state")
        store.db.execute("DELETE FROM boots")
    for index, node in enumerate(ROOMS):
        stop = [0, 0, 5, 24][index]  # Demonstrate fresh, delayed and offline rooms.
        for minute in range(24 * 60, stop - 1, -1):
            stamp = now - minute * 60
            sequence = 24 * 60 - minute
            store.ingest(packet(node, sequence, stamp), received_at=stamp)


def tick(store):
    now = store.clock()
    for node in list(ROOMS)[:2]:
        with store.lock:
            previous = store.db.execute("SELECT sequence FROM node_state WHERE node_id=?", (node,)).fetchone()
        store.ingest(packet(node, previous[0] + 1, now))

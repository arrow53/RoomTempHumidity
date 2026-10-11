"""Small bounded SQLite store. All access is serialized across HTTP/CoAP threads."""
import json
import math
import sqlite3
import threading
import time
from pathlib import Path

from .protocol import NODE_ID, ReadingError, fingerprint, parse_reading


def load_rooms(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or len(data) > 128:
        raise ValueError("rooms must be an object with at most 128 nodes")
    for node, label in data.items():
        if not NODE_ID.fullmatch(node) or not isinstance(label, str) or not 1 <= len(label.strip()) <= 60:
            raise ValueError("each room needs a valid node ID and 1-60 character label")
    return {node: label.strip() for node, label in data.items()}


class Store:
    def __init__(self, path, mode, rooms, retention_days=30, max_rows=50000,
                 fresh_s=180, offline_s=600, clock=time.time, max_boots=1024):
        if mode not in ("live", "demo"):
            raise ValueError("invalid mode")
        if not (0 < retention_days <= 3650 and math.isfinite(retention_days)):
            raise ValueError("retention_days must be > 0 and <= 3650")
        if type(max_rows) is not int or not 1 <= max_rows <= 1000000:
            raise ValueError("max_rows must be 1-1000000 per node")
        if type(max_boots) is not int or not 2 <= max_boots <= 10000:
            raise ValueError("max_boots must be 2-10000 per node")
        if not 0 < fresh_s < offline_s:
            raise ValueError("require 0 < fresh_s < offline_s")
        if len(rooms) > 128 or any(not NODE_ID.fullmatch(n) for n in rooms):
            raise ValueError("invalid room configuration")
        self.mode, self.rooms, self.clock = mode, dict(rooms), clock
        self.retention_s, self.max_rows = retention_days * 86400, max_rows
        self.max_boots = max_boots
        self.fresh_s, self.offline_s = fresh_s, offline_s
        self.lock = threading.RLock()
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        try:
            self.db.execute("PRAGMA journal_mode=WAL")
            self.db.execute("PRAGMA busy_timeout=5000")
            self.db.executescript("""
                CREATE TABLE IF NOT EXISTS metadata(key TEXT PRIMARY KEY, value TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS node_state(
                    node_id TEXT PRIMARY KEY, sequence INTEGER NOT NULL, uptime_s INTEGER NOT NULL,
                    digest TEXT NOT NULL, received_at REAL NOT NULL, boot_id TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS boots(node_id TEXT NOT NULL, boot_id TEXT NOT NULL,
                    sequence INTEGER NOT NULL, digest TEXT NOT NULL, received_at REAL NOT NULL,
                    PRIMARY KEY(node_id,boot_id));
                CREATE TABLE IF NOT EXISTS readings(
                    id INTEGER PRIMARY KEY, node_id TEXT NOT NULL, received_at REAL NOT NULL,
                    sequence INTEGER NOT NULL, uptime_s INTEGER NOT NULL,
                    temperature_c REAL NOT NULL, humidity_pct REAL NOT NULL, boot_id TEXT NOT NULL,
                    digest TEXT NOT NULL, UNIQUE(node_id,boot_id,sequence));
                CREATE INDEX IF NOT EXISTS readings_node_time ON readings(node_id, received_at, id);
                CREATE INDEX IF NOT EXISTS readings_time ON readings(received_at);
            """)
            with self.db:
                row = self.db.execute("SELECT value FROM metadata WHERE key='mode'").fetchone()
                if row and row[0] != mode:
                    raise ValueError("database mode mismatch: demo and live must use separate databases")
                self.db.execute("INSERT OR IGNORE INTO metadata VALUES('mode', ?)", (mode,))
                version = self.db.execute("SELECT value FROM metadata WHERE key='version'").fetchone()
                if version and version[0] != "3":
                    raise ValueError("unsupported database version; use a new database for the boot_id contract")
                self.db.execute("INSERT OR IGNORE INTO metadata VALUES('version','3')")
                # Removing a node from the allowlist also removes its stored data/state.
                for node, in self.db.execute("SELECT node_id FROM node_state").fetchall():
                    if node not in self.rooms:
                        self.db.execute("DELETE FROM readings WHERE node_id=?", (node,))
                        self.db.execute("DELETE FROM node_state WHERE node_id=?", (node,))
                        self.db.execute("DELETE FROM boots WHERE node_id=?", (node,))
            self.prune()
        except Exception:
            self.db.close()
            raise

    def ingest(self, payload, received_at=None):
        reading = parse_reading(payload)
        node = reading["node_id"]
        if node not in self.rooms:
            raise ReadingError("node is not configured in rooms file", "unknown_node")
        now = self.clock() if received_at is None else received_at
        digest = fingerprint(reading)
        with self.lock, self.db:
            previous = self.db.execute("SELECT * FROM node_state WHERE node_id=?", (node,)).fetchone()
            prior_sample = self.db.execute("SELECT digest,received_at FROM readings WHERE node_id=? AND boot_id=? AND sequence=?",
                                           (node, reading["boot_id"], reading["sequence"])).fetchone()
            boot = self.db.execute("SELECT * FROM boots WHERE node_id=? AND boot_id=?", (node, reading["boot_id"])).fetchone()
            retry = prior_sample or (boot if boot and boot["sequence"] == reading["sequence"] else None)
            if retry:
                if digest == retry["digest"]:
                    return {"status": "duplicate", "received_at": retry["received_at"]}
                raise ReadingError("conflicting duplicate reading identity", "replay")
            same_boot = previous and previous["boot_id"] == reading["boot_id"]
            if previous and now < previous["received_at"]:
                raise ReadingError("collector clock moved backwards; correct host time", "clock")
            if same_boot:
                if reading["sequence"] <= previous["sequence"] or reading["uptime_s"] < previous["uptime_s"]:
                    raise ReadingError("counter regression or conflicting duplicate within a boot", "replay")
            else:
                if boot:
                    raise ReadingError("reading is from a retired boot", "replay")
                count = self.db.execute("SELECT count(*) FROM boots WHERE node_id=?", (node,)).fetchone()[0]
                if count >= self.max_boots:
                    raise ReadingError("boot ledger full; verify node before reset-node", "boot_limit")
            self.db.execute("INSERT OR REPLACE INTO boots VALUES(?,?,?,?,?)", (node, reading["boot_id"], reading["sequence"], digest, now))
            self.db.execute("INSERT INTO readings(node_id,received_at,sequence,uptime_s,temperature_c,humidity_pct,boot_id,digest) VALUES(?,?,?,?,?,?,?,?)",
                            (node, now, reading["sequence"], reading["uptime_s"], reading["temperature_c"], reading["humidity_pct"], reading["boot_id"], digest))
            self.db.execute("INSERT OR REPLACE INTO node_state VALUES(?,?,?,?,?,?)",
                            (node, reading["sequence"], reading["uptime_s"], digest, now, reading["boot_id"]))
            self._prune(now, node)
        return {"status": "stored", "received_at": now}

    def _prune(self, now, node=None):
        self.db.execute("DELETE FROM readings WHERE received_at < ?", (now - self.retention_s,))
        for name in ([node] if node else self.rooms):
            self.db.execute("""DELETE FROM readings WHERE node_id=? AND id NOT IN
                (SELECT id FROM readings WHERE node_id=? ORDER BY received_at DESC,id DESC LIMIT ?)""",
                            (name, name, self.max_rows))

    def prune(self):
        with self.lock, self.db:
            self._prune(self.clock())

    def reset_node(self, node):
        if node not in self.rooms:
            raise ValueError("unknown node")
        with self.lock, self.db:
            self.db.execute("DELETE FROM node_state WHERE node_id=?", (node,))
            self.db.execute("DELETE FROM boots WHERE node_id=?", (node,))

    def summary(self):
        now = self.clock()
        rooms = []
        with self.lock:
            for node, label in self.rooms.items():
                row = self.db.execute("SELECT * FROM readings WHERE node_id=? AND received_at>=? ORDER BY received_at DESC,id DESC LIMIT 1",
                                      (node, now - self.retention_s)).fetchone()
                item = {"node_id": node, "label": label, "status": "waiting", "age_s": None,
                        "temperature_c": None, "humidity_pct": None, "received_at": None}
                if row:
                    age = now - row["received_at"]
                    status = "clock_error" if age < -1 else "fresh" if age <= self.fresh_s else "stale" if age <= self.offline_s else "offline"
                    item.update({key: row[key] for key in ("temperature_c", "humidity_pct", "received_at")})
                    item.update(status=status, age_s=max(0, age))
                rooms.append(item)
        return {"mode": self.mode, "server_time": now, "fresh_s": self.fresh_s,
                "offline_s": self.offline_s, "retention_days": self.retention_s / 86400, "rooms": rooms}

    def history(self, node, hours=24, limit=240):
        if node not in self.rooms:
            raise ValueError("unknown node")
        if not math.isfinite(hours) or not 0 < hours <= min(87600, self.retention_s / 3600):
            raise ValueError("hours is outside configured retention")
        if type(limit) is not int or not 2 <= limit <= 1000:
            raise ValueError("limit must be 2-1000")
        end = self.clock()
        start = end - hours * 3600
        width = hours * 3600 / limit
        with self.lock:
            # Bound response size and SQL work; bucket means aren't raw samples.
            rows = self.db.execute("""SELECT AVG(received_at) AS received_at,
                AVG(temperature_c) AS temperature_c, AVG(humidity_pct) AS humidity_pct,
                COUNT(*) AS samples FROM readings WHERE node_id=? AND received_at>=? AND received_at<=?
                GROUP BY MIN(?, CAST((received_at - ?) / ? AS INTEGER)) ORDER BY received_at""",
                (node, start, end, limit - 1, start, width)).fetchall()
        return {"node_id": node, "from": start, "to": end, "aggregation": "bucket_mean",
                "bucket_seconds": width, "points": [dict(row) for row in rows]}

    def close(self):
        with self.lock:
            self.db.close()

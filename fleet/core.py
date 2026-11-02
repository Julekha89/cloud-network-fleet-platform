"""Deterministic simulated network inventory and read-only health assessment."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
import sqlite3
import threading

STATUSES = {'healthy', 'degraded', 'offline'}

@dataclass(frozen=True)
class Device:
    device_id: str
    hostname: str
    region: str
    device_type: str
    simulated_status: str


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class FleetStore:
    """SQLite-backed inventory with append-only assessment audit records."""
    def __init__(self, database: str | Path = ':memory:'):
        self.connection = sqlite3.connect(str(database), check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.lock = threading.RLock()
        with self.lock, self.connection:
            self.connection.execute('CREATE TABLE IF NOT EXISTS devices (device_id TEXT PRIMARY KEY, hostname TEXT NOT NULL, region TEXT NOT NULL, device_type TEXT NOT NULL, simulated_status TEXT NOT NULL)')
            self.connection.execute('CREATE TABLE IF NOT EXISTS audit (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp_utc TEXT NOT NULL, action TEXT NOT NULL, device_id TEXT NOT NULL, result TEXT NOT NULL)')

    def add(self, device: Device) -> None:
        if not device.device_id or not device.hostname or not device.region or not device.device_type or device.simulated_status not in STATUSES:
            raise ValueError('Invalid simulated device')
        with self.lock, self.connection:
            self.connection.execute('INSERT INTO devices VALUES (?, ?, ?, ?, ?)', (device.device_id, device.hostname, device.region, device.device_type, device.simulated_status))
            self.connection.execute('INSERT INTO audit (timestamp_utc,action,device_id,result) VALUES (?,?,?,?)', (utc_now(), 'onboard', device.device_id, 'accepted'))

    def list_devices(self, region: str | None = None) -> list[dict]:
        with self.lock:
            if region:
                records = self.connection.execute('SELECT * FROM devices WHERE region=? ORDER BY device_id', (region,)).fetchall()
            else:
                records = self.connection.execute('SELECT * FROM devices ORDER BY device_id').fetchall()
        return [dict(record) for record in records]

    def assess(self, device_id: str) -> dict | None:
        with self.lock, self.connection:
            row = self.connection.execute('SELECT * FROM devices WHERE device_id=?', (device_id,)).fetchone()
            if row is None:
                return None
            status = row['simulated_status']
            result = {'device_id': device_id, 'region': row['region'], 'status': status, 'checked_at': utc_now(), 'source': 'simulated'}
            self.connection.execute('INSERT INTO audit (timestamp_utc,action,device_id,result) VALUES (?,?,?,?)', (result['checked_at'], 'health_check', device_id, status))
        return result

    def summary(self) -> dict:
        rows = self.list_devices()
        return {'total': len(rows), 'by_status': {status: sum(d['simulated_status'] == status for d in rows) for status in sorted(STATUSES)}, 'by_region': {region: sum(d['region'] == region for d in rows) for region in sorted({d['region'] for d in rows})}, 'source': 'simulated'}

    def audit_log(self, limit: int = 50) -> list[dict]:
        with self.lock:
            records = self.connection.execute('SELECT * FROM audit ORDER BY id DESC LIMIT ?', (max(1, min(limit, 100)),)).fetchall()
        return [dict(row) for row in records]

    def close(self) -> None:
        self.connection.close()


def load_sample(store: FleetStore, sample_path: str | Path) -> int:
    devices = json.loads(Path(sample_path).read_text(encoding='utf-8'))
    for record in devices:
        store.add(Device(**record))
    return len(devices)

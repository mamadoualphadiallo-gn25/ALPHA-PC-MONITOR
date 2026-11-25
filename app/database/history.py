from pathlib import Path
import sqlite3

class HistoryStore:
    def __init__(self, path):
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS samples (
                id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT NOT NULL,
                cpu REAL NOT NULL, ram REAL NOT NULL, net_down REAL NOT NULL,
                net_up REAL NOT NULL, disk_read REAL NOT NULL, disk_write REAL NOT NULL)''')
            db.execute("CREATE INDEX IF NOT EXISTS idx_samples_timestamp ON samples(timestamp)")
    def _connect(self):
        db = sqlite3.connect(self.path, timeout=5)
        db.execute("PRAGMA journal_mode=WAL")
        return db
    def add(self, s):
        with self._connect() as db:
            db.execute("INSERT INTO samples(timestamp,cpu,ram,net_down,net_up,disk_read,disk_write) VALUES(?,?,?,?,?,?,?)",
                (s["timestamp"],s["cpu_percent"],s["ram_percent"],s["net_down_bps"],s["net_up_bps"],s["disk_read_bps"],s["disk_write_bps"]))
    def recent(self, limit=300):
        with self._connect() as db:
            return db.execute("SELECT timestamp,cpu,ram,net_down,net_up,disk_read,disk_write FROM samples ORDER BY id DESC LIMIT ?",(max(1,min(int(limit),100000)),)).fetchall()

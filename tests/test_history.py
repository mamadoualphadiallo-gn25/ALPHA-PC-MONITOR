from app.database.history import HistoryStore

def test_history_roundtrip(tmp_path):
    db=HistoryStore(tmp_path/"history.sqlite3")
    sample={"timestamp":"2026-01-01T00:00:00+00:00","cpu_percent":12.0,"ram_percent":40.0,"net_down_bps":1.0,"net_up_bps":2.0,"disk_read_bps":3.0,"disk_write_bps":4.0}
    db.add(sample)
    rows=db.recent()
    assert len(rows)==1 and rows[0][1]==12.0

from app.core.collector import SystemCollector

def test_collector_returns_real_measurement_fields():
    data=SystemCollector().collect()
    assert 0 <= data["cpu_percent"] <= 100
    assert data["ram_total"] > 0
    assert data["uptime_seconds"] >= 0
    assert isinstance(data["disks"],list)

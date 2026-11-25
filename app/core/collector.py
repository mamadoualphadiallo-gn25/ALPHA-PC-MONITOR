from __future__ import annotations
import platform, socket, time
from datetime import datetime, timezone
from typing import Any
import psutil

class SystemCollector:
    """Collecte locale. Les informations indisponibles sont None, jamais inventées."""
    def __init__(self):
        self._net = psutil.net_io_counters()
        self._net_time = time.monotonic()
        self._disk = psutil.disk_io_counters()
        self._disk_time = time.monotonic()
        psutil.cpu_percent(interval=None, percpu=True)

    def collect(self) -> dict[str, Any]:
        now = time.monotonic()
        cores = psutil.cpu_percent(interval=None, percpu=True)
        cpu = sum(cores) / len(cores) if cores else 0.0
        vm, swap = psutil.virtual_memory(), psutil.swap_memory()
        boot = datetime.fromtimestamp(psutil.boot_time()).astimezone()
        net = psutil.net_io_counters()
        dt = max(now - self._net_time, 0.001)
        down = max(0, net.bytes_recv - self._net.bytes_recv) / dt
        up = max(0, net.bytes_sent - self._net.bytes_sent) / dt
        self._net, self._net_time = net, now
        disk = psutil.disk_io_counters()
        ddt = max(now - self._disk_time, 0.001)
        read = max(0, disk.read_bytes - self._disk.read_bytes) / ddt if disk and self._disk else 0.0
        write = max(0, disk.write_bytes - self._disk.write_bytes) / ddt if disk and self._disk else 0.0
        self._disk, self._disk_time = disk, now
        partitions = []
        for part in psutil.disk_partitions(all=False):
            try:
                u = psutil.disk_usage(part.mountpoint)
                partitions.append({"device":part.device,"mountpoint":part.mountpoint,"fstype":part.fstype,
                    "total":u.total,"used":u.used,"free":u.free,"percent":u.percent})
            except (OSError, PermissionError):
                continue
        freq = psutil.cpu_freq()
        try: host = socket.gethostname()
        except OSError: host = platform.node()
        return {
            "timestamp":datetime.now(timezone.utc).isoformat(), "host":host,
            "os":f"{platform.system()} {platform.release()}",
            "uptime_seconds":max(0,time.time()-psutil.boot_time()), "boot_time":boot.isoformat(timespec="seconds"),
            "cpu_percent":cpu,"cpu_per_core":cores,"cpu_count_physical":psutil.cpu_count(logical=False),
            "cpu_count_logical":psutil.cpu_count(logical=True),"cpu_frequency_mhz":freq.current if freq else None,
            "ram_total":vm.total,"ram_used":vm.used,"ram_available":vm.available,"ram_percent":vm.percent,
            "swap_total":swap.total,"swap_used":swap.used,"swap_percent":swap.percent,
            "process_count":len(psutil.pids()),"disks":partitions,
            "disk_read_bps":read,"disk_write_bps":write,"net_down_bps":down,"net_up_bps":up,
            "net_bytes_recv":net.bytes_recv,"net_bytes_sent":net.bytes_sent,
            "gpu_name":None,"gpu_percent":None,"gpu_note":"Interface GPU dédiée non intégrée dans cette version.",
            "temperature_cpu":None,"temperature_gpu":None,
            "temperature_note":"Capteurs thermiques non interrogés dans cette version."
        }

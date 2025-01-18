import time
import psutil
from typing import Dict


class Computer:
    def get_stats_dict() -> Dict[str, object]:
        """
        Aggregates all system statistics into a dictionary.
        Returns values in a human readable format (GHz for CPU, GB for memory/disk).
        """
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        cpu_freq = psutil.cpu_freq()

        stats_dict = {
            "cpu_count": psutil.cpu_count(logical=True),
            "cpu_usage": psutil.cpu_percent(percpu=False),  # Use small interval for more accurate reading
            "cpu_frequency": {
                "current_frequency": round(cpu_freq.current / 1000, 1),  # Convert MHz to GHz
                "max_frequency": cpu_freq.max,
            },
            "ram_total": round(memory.total / (1024**3), 2),  # Convert bytes to GB
            "ram_available": round(memory.available / (1024**3), 2),
            "ram_percentage": memory.percent,
            "disk_total": round(disk.total / (1024**3), 2),
            "disk_free": round(disk.free / (1024**3), 2),
            "disk_used": disk.percent,
            "disk_percentage": disk.percent,
        }

        try:
            temps = psutil.sensors_temperatures()
            if temps:
                stats_dict["core_temperatures"] = {
                    sensor.label: sensor.current for device in temps.values() for sensor in device
                }
            else:
                stats_dict["core_temperatures"] = {}
        except AttributeError:
            stats_dict["core_temperatures"] = {}

        return stats_dict


if __name__ == "__main__":
    while True:
        print(Computer.get_stats_dict())
        time.sleep(1)

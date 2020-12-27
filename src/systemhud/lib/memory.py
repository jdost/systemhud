from dataclasses import dataclass
from pathlib import Path


class Memory:
    PROC_MEMINFO = Path("/proc/meminfo")

    def init(self):
        self.update()

    def update(self) -> None:
        with self.PROC_MEMINFO.open() as proc_meminfo:
            for line in proc_meminfo:
                if ":" not in line:
                    continue

                k, v_str = line.split(":", 1)
                k = k.strip()
                v = int(v_str.rstrip(" kB\n"))

                if k == "MemTotal":
                    self.total = v
                elif k == "MemFree":
                    self.free = v
                elif k == "Buffers":
                    self.buffered = v
                elif k == "Cached":
                    self.cached = v

    @property
    def used(self) -> int:
        return self.total - self.free + self.buffered + self.cached

    @property
    def perc_used(self) -> float:
        return self.used / self.total

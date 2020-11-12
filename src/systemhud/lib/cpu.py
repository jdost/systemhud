from dataclasses import dataclass
from os import cpu_count
from typing import Sequence

PROC_STAT = "/proc/stat"


@dataclass
class CPU:
    user: int
    nice: int
    system: int
    idle: int
    iowait: int
    irq: int
    softirq: int
    steal: int
    guest: int
    guest_nice: int

    @classmethod
    def get(cls, cpu_num=-1) -> "CPU":
        target_line_no = cpu_num + 1
        with open(PROC_STAT, "r") as proc_stat:
            line_no = 0
            for line in proc_stat:
                if line_no == target_line_no:
                    raw_line = line
                    break

                line_no += 1

        return cls(*map(int, raw_line.split()[1:]))

    @classmethod
    def get_all(cls) -> Sequence["CPU"]:
        return [cls.get(n) for n in range(-1, cpu_count() or 1)]

    @property
    def total(self) -> int:
        return sum(
            [
                self.user,
                self.nice,
                self.system,
                self.idle,
                self.iowait,
                self.steal,
            ]
        )

    @property
    def usage(self) -> int:
        return self.total - self.idle


CHECKPOINT = CPU.get_all()


class CPUDiff:
    def __init__(self, st: CPU, ed: CPU):
        self.usage = ed.usage - st.usage
        self.user = ed.user - st.user
        self.system = ed.system - st.system
        self.nice = ed.nice - st.nice
        self.iowait = ed.iowait - st.iowait
        self.steal = ed.steal - st.steal
        self.total = ed.total - st.total

    @property
    def usage_percent(self) -> float:
        if self.total == 0:
            return 0.0

        return self.usage / self.total

    def __str__(self) -> str:
        return "{:06.2%}".format(self.usage_percent)


def diffs(update: bool = False) -> Sequence[CPUDiff]:
    global CHECKPOINT
    if not CHECKPOINT:
        CHECKPOINT = CPU.get_all()

    new_checkpoint = CPU.get_all()
    diffs = [
        CPUDiff(cp, new_cp) for cp, new_cp in zip(CHECKPOINT, new_checkpoint)
    ]

    if update:
        CHECKPOINT = new_checkpoint

    return diffs

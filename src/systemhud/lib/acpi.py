from enum import Enum
from pathlib import Path
from typing import Optional

from systemhud.streams import capture


class Status(Enum):
    FULL = "Full"
    DISCHARGING = "Discharging"
    CHARGING = "Charging"
    UNKNOWN = "Unknown"

    @classmethod
    def get(cls, i: str) -> "Status":
        k = i.upper()
        return cls[k]


class Battery:
    DEV_PATH = Path("/sys/class/power_supply")
    _status: Optional[Status]
    _capacity: Optional[int]

    def __init__(self, bat_name: str = "BAT0"):
        self.path = Battery.DEV_PATH / bat_name
        self.uncache()

    def uncache(self) -> None:
        self._status = None
        self._capacity = None

    @property
    def status(self) -> Status:
        if self._status is None:
            self._status = Status.get(
                (self.path / "status").read_text().strip()
            )

        return self._status

    @property
    def capacity(self) -> int:
        if self._capacity is None:
            self._capacity = int((self.path / "capacity").read_text())

        return self._capacity

    @property
    async def remaining(self) -> str:
        if self.status is Status.FULL:
            return ""
        elif self.status is Status.UNKNOWN:
            return "UNKNOWN"

        acpi_output = "\n".join(await capture("acpi -b"))
        return acpi_output.rsplit(",", 1)[1].strip().split(" ", 1)[0]

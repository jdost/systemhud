import datetime
from typing import List, Optional

from systemhud.streams import capture

APT_FORMAT = "%S %m\n"


class Appointment:
    name: str
    start: datetime.datetime
    FULL_DAY_FMT = "..:.."

    def __init__(self, date: datetime.date, event: str):
        time, name = event.split(" ", 1)
        self.name = name
        if time == self.FULL_DAY_FMT:
            time = "00:00"
        self.start = datetime.datetime.combine(
            date,
            datetime.datetime.strptime(time, "%H:%M").time(),
        )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.start} - {self.name}>"

    def __gt__(self, other: datetime.datetime) -> bool:
        return self.start > other


max_appointment = Appointment(datetime.date.max, "00:00 MAX FUTURE")


async def get_appointments(days: int = 1) -> List[Appointment]:
    date: Optional[datetime.date] = None
    appointments: List[Appointment] = []

    for line in await capture(
        f'calcurse -Q --filter-type cal --days {days} --format-apt="{APT_FORMAT}"'
    ):
        if date is None:
            date = datetime.datetime.strptime(line, "%m/%d/%y:").date()
        elif not line:
            date = None
        else:
            appointments.append(Appointment(date, line))

    return appointments

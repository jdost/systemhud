import datetime
from typing import List, Sequence

from systemhud.ui.pango import wrapped

SUNDAY = 6


class Calendar:
    SCHEDULED = wrapped(foreground="00FFFF")
    TODAY = wrapped(weight="bold", foreground="00FF00")
    ACTIVE = wrapped(foreground="FFFFFF")
    INACTIVE = wrapped(foreground="333333")

    def __init__(self, date: datetime.datetime):
        self.base = date

    @property
    def label(self) -> str:
        return self.base.strftime("%B")

    def rows(self, schedule: Sequence[datetime.date] = []) -> Sequence[str]:
        rows: List[str] = []
        row = ""

        first = datetime.date(self.base.year, self.base.month, 1)
        # weekday() treats weeks to be [M...SUN], so we adjust, a month
        # starting on a sunday ends up putting an empty week here, so we
        # special case that
        if first.weekday() == SUNDAY:
            cursor = first
        else:
            # and then adjust the rest to be on the preceeding sunday
            cursor = first - datetime.timedelta(days=first.weekday() + 1)
        while True:
            if cursor == self.base.date():
                tag = Calendar.TODAY
            elif cursor in schedule:
                tag = Calendar.SCHEDULED
            elif cursor.month != self.base.month:
                tag = Calendar.INACTIVE
            else:
                tag = Calendar.ACTIVE
            row += tag(f"{cursor.day:2}") + " "
            cursor += datetime.timedelta(days=1)
            if cursor.weekday() == SUNDAY:
                rows.append(row.rstrip())
                row = ""
                if cursor.month != first.month:
                    break
            elif cursor < first:
                continue

        return rows

    def __str__(self) -> str:
        return "\n".join(self.rows())

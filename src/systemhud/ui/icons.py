from sys import stdout
from typing import Sequence


class ProgressiveValue:
    def __init__(self, progression: Sequence[str]):
        self.progression = progression
        self._length = len(progression)

    def __call__(self, v: int) -> str:
        idx = int(v / 100 * self._length)
        return self.progression[min(idx, self._length - 1)]


def set_icon(icon: str) -> None:
    print(icon)
    stdout.flush()


class EqDots:
    ICONS: Sequence[str] = "⡀⠄⠂⠁"
    LEVELS: Sequence[int] = [0, 25, 50, 75]
    COLORS: Sequence[str] = ["F00", "F60", "FF0", "0C0"]
    ZERO_COLOR: str = "666"

    def __init__(
        self,
        levels: Sequence[int] = [],
        colors: Sequence[str] = [],
        zero_color: str = "",
    ):
        self.levels = levels if levels else EqDots.LEVELS
        self.colors = colors if colors else EqDots.COLORS
        self.zero_color = zero_color or EqDots.ZERO_COLOR

    def __call__(self, v: int) -> str:
        if v == 0:
            return f"%{{F#{self.zero_color}}}{self.ICONS[0]}%{{F-}}"

        dots = ""
        for threshold, color, icon in zip(self.levels, self.colors, self.ICONS):
            if v > threshold:
                if dots:
                    dots += "%{O-11}"
                dots += f"%{{F#{color}}}{icon}%{{F-}}"

        return dots


dots = EqDots()

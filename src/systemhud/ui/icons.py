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
    LEVELS: Sequence[int] = [0, 25, 50, 75, 100]
    COLORS: Sequence[str] = ["FF0000", "FF6600", "FFFF00", "00FF00"]
    ZERO_COLOR: str = "666"

    def __init__(
        self,
        # the default being an empty list is me being lazy in typing, it keeps
        # the typing consistent and the value is falsey which instead uses a
        # default that *isn't* the shared reference
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
        for min_threshold, max_threshold, color, icon in \
            zip(self.levels, self.levels[1:], self.colors, self.ICONS):
            if v > max_threshold:
                if dots:
                    dots += "%{O-11}"
                dots += f"%{{F#{color}}}{icon}%{{F-}}"
            elif v > min_threshold:
                # when in the final threshold bracket, we apply an opacity
                # to the dot, ranging from 50% to 100% (lower opacities were
                # barely noticeable)
                if dots:
                    dots += "%{O-11}"
                # basically 8*(percent between min and max) + 8
                internal_bracket = int((v - min_threshold) * 8 / (max_threshold - min_threshold)) + 8
                # The opacity needs to be 2 characters, I also uppercase it to
                # be consistent with the other hex characters
                opacity = hex(internal_bracket - 1)[-1].upper() * 2
                dots += f"%{{F#{opacity}{color}}}{icon}%{{F-}}"
                break

        return dots


dots = EqDots()

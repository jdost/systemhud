import os
from enum import Enum
from typing import Optional, Sequence, Union

from systemhud.ui import colors

THEME = os.environ.get("ICON_THEME", "")


class BaseIcon:
    def __init__(
        self,
        char: str,
        fg: Optional[colors.Color] = None,
        bg: Optional[colors.Color] = None,
        offset: Union[bool, int, None] = None,
        underline: Union[bool, colors.Color, None] = None,
    ):
        self.icon = char
        self.fg = fg
        self.bg = bg
        self.offset = 11 if offset is True else offset
        self.underline = underline

    def __repr__(self) -> str:
        out = f"<Icon({self.icon}"
        out += f",fg:{self.fg}" if self.fg else ""
        out += f",bg:{self.bg}" if self.bg else ""
        out += f",off:{self.offset}" if self.offset else ""
        if self.underline:
            out += f",ul"
            if isinstance(self.underline, colors.Color):
                out += f":{self.underline}"

        return out + ")>"

    def __str__(self) -> str:
        out = self.icon
        if self.offset:
            out = f"  %{{O-{self.offset}}}{out} %{{O-{self.offset}}}"
        if self.fg:
            out = f"%{{F#{self.fg}}}{out}%{{F-}}"
        if self.bg:
            out = f"%{{B#{self.bg}}}{out}%{{B-}}"
        if self.underline:
            out = f"%{{+u}}{out}%{{-u}}"
            if isinstance(self.underline, colors.Color):
                out = f"%{{u{self.underline}}}{out}%{{u-}}"

        return out


class Icon(BaseIcon):
    def __call__(
        self,
        foreground: Optional[colors.Color] = None,
        background: Optional[colors.Color] = None,
        offset: Union[bool, int, None] = None,
        underline: Union[bool, colors.Color, None] = None,
    ) -> "Icon":
        return self.__class__(
            self.icon,
            fg=foreground if foreground else self.fg,
            bg=background if background else self.bg,
            offset=offset if offset else self.offset,
            underline=underline if underline else self.underline,
        )


class ProgressiveIcon(BaseIcon):
    def __init__(self, progression: Sequence[str]):
        self.progression = progression
        self._length = len(progression)

    def __call__(self, v: Union[int, float]) -> BaseIcon:
        if isinstance(v, int):
            idx = int(v / 100 * self._length)
        else:
            idx = int(v * self._length)
        return Icon(self.progression[min(idx, self._length - 1)])


class GradientIcon(BaseIcon):
    GYR_GRADIENT = colors.GYR_GRADIENT
    RYG_GRADIENT = colors.RYG_GRADIENT
    DEFAULT_GRADIENT = colors.GYR_GRADIENT

    def __init__(
        self, char: str, fg_gradient: Optional[colors.GradientColor] = None
    ):
        self.fg_gradient = fg_gradient if fg_gradient else self.DEFAULT_GRADIENT
        super().__init__(char)

    def __call__(self, v: Union[int, float]) -> BaseIcon:
        return BaseIcon(
            self.icon,
            fg=self.fg_gradient(v),
            bg=self.bg,
            offset=self.offset,
            underline=self.underline,
        )


class EqDotsIcon(BaseIcon):
    ICONS: Sequence[str] = "⡀⠄⠂⠁"
    LEVELS: Sequence[int] = [0, 25, 50, 75, 100]
    COLORS: Sequence[colors.Color] = [
        colors.RED,
        colors.ORANGE,
        colors.YELLOW,
        colors.GREEN,
    ]
    ZERO_COLOR: colors.Color = colors.DARK_GREY

    def __init__(
        self,
        # the default being an empty list is me being lazy in typing, it keeps
        # the typing consistent and the value is falsey which instead uses a
        # default that *isn't* the shared reference
        levels: Sequence[int] = [],
        colors: Sequence[colors.Color] = [],
        zero_color: Optional[colors.Color] = None,
        value: Union[int, float] = 0,
    ):
        self.value = value
        self.levels = levels if levels else self.LEVELS
        self.colors = colors if colors else self.COLORS
        self.zero_color = zero_color or self.ZERO_COLOR

    def __call__(self, v: Union[int, float]) -> "EqDotsIcon":
        return self.__class__(
            levels=self.levels,
            colors=self.colors,
            zero_color=self.zero_color,
            value=v,
        )

    def __str__(self) -> str:
        if self.value == 0:
            return f"%{{F{self.zero_color}}}{self.ICONS[0]}%{{F-}}"

        dots = ""
        for min_threshold, max_threshold, color, icon in zip(
            self.levels, self.levels[1:], self.colors, self.ICONS
        ):
            if self.value > max_threshold:
                if dots:
                    dots += "%{O-11}"
                dots += f"%{{F{color}}}{icon}%{{F-}}"
            elif self.value > min_threshold:
                # when in the final threshold bracket, we apply an opacity
                # to the dot, ranging from 50% to 100% (lower opacities were
                # barely noticeable)
                if dots:
                    dots += "%{O-11}"
                # basically 8*(percent between min and max) + 8
                internal_bracket = (
                    int(
                        (self.value - min_threshold)
                        * 8
                        / (max_threshold - min_threshold)
                    )
                    + 8
                )
                dots += f"%{{F#{color.with_opacity(internal_bracket)}}}{icon}%{{F-}}"
                break

        return dots


class EnumIcon(Icon, Enum):
    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return repr(self.value)

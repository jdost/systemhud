from typing import Optional, Sequence, Tuple, Union


def parse_color_str(src: str) -> Tuple[int, int, int, float]:
    if len(src) in {3, 4}:
        src = "".join(c * 2 for c in src)
    elif len(src) not in {6, 8}:
        raise ValueError(
            "color strings can only be in the format: "
            "[RGB, RGBO, RRGGBB, RRGGBBOO]"
        )

    r = int(src[0:2], 16)
    g = int(src[2:4], 16)
    b = int(src[4:6], 16)
    if len(src) in {4, 8}:
        o = int(src[6:8], 16) / 255
    else:
        o = 1.0

    return r, g, b, o


def validate_color_value(*values: int) -> None:
    for v in values:
        assert (
            v >= 0 and v < 256
        ), f"{v} is not a valid color, must be within the range [0,255]."


class Color:
    HEX_STR_FORMAT = "{:02X}{:02X}{:02X}{:02X}"

    def __init__(
        self,
        r_or_color: Union[str, int],
        g: Optional[int] = None,
        b: Optional[int] = None,
        o: float = 1.0,
    ):
        if isinstance(r_or_color, str):
            self._red, self._green, self._blue, self._opacity = parse_color_str(
                r_or_color
            )
        elif g is None or b is None:
            raise ValueError(
                "You must pass in a red, green, and blue value for a Color."
            )
        else:
            self._red = r_or_color
            self._green = g
            self._blue = b
            self._opacity = o

        validate_color_value(self._red, self._green, self._blue)
        assert self._opacity >= 0.0 and self._opacity <= 1.0, (
            f"{self._opacity} is not within the valid opacity range "
            "of [0.0,1.0]."
        )

    def __str__(self) -> str:
        return self.HEX_STR_FORMAT.format(
            int(self._opacity * 255), self._red, self._green, self._blue
        )

    def __repr__(self) -> str:
        return (
            f"<Color ({self._red},{self._green},{self._blue},{self._opacity})>"
        )

    def with_opacity(self, new_opacity: Union[int, float]) -> "Color":
        if isinstance(new_opacity, float):
            return Color(self._red, self._green, self._blue, new_opacity)
        if new_opacity > 100 or new_opacity < 0:
            raise ValueError(
                f"{new_opacity} is not within the valid range of [0, 100]"
            )

        return Color(self._red, self._green, self._blue, new_opacity / 100.0)


class GradientColor:
    def __init__(self, gradient: Sequence[Color]):
        self.gradient = gradient

    def reversed(self) -> "GradientColor":
        return self.__class__(self.gradient[::-1])

    def __call__(self, value: Union[int, float]) -> Color:
        if isinstance(value, int):
            idx = int(value / 100 * len(self.gradient))
        else:
            idx = int(value * len(self.gradient))

        return self.gradient[min(idx, len(self.gradient) - 1)]


CLEAR = Color(0, 0, 0, 0.0)
RED = Color(255, 0, 0)
GREEN = Color(0, 255, 0)
BLUE = Color(0, 0, 255)
YELLOW = Color(255, 255, 0)
WHITE = Color(255, 255, 255)
ORANGE = Color(255, 102, 0)
GREY = Color(153, 153, 153)
DARK_GREY = Color(102, 102, 102)
CYAN = Color(85, 170, 255)
# Gradients, the idea is providing a stepped set of colors in a sequence
GYR_GRADIENT = GradientColor(
    [Color(int(i * 255 / 9), 204 + int(i * 51 / 9), 0) for i in range(10)]
    + [Color(255, 255 - int(i * 255 / 10), 0) for i in range(1, 11)]
)
RYG_GRADIENT = GYR_GRADIENT.reversed()

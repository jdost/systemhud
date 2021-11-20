RED = "FF0000"
GREEN = "00FF00"
YELLOW = "FFFF00"
ORANGE = "FF6600"
DARK_GREY = "666666"
GREY = "999999"
CYAN = "55AAFF"
WHITE = "FFFFFF"


def with_opacity(base: str, opacity: float) -> str:
    if opacity > 1 or opacity < 0:
        raise ValueError(f"Opacity must be between 0 and 1.0, got: {opacity}")

    if len(base) == 0:
        return ""
    if len(base) == 3:
        return f"{hex(int(opacity * 16))[2:].upper()}{base}"
    elif len(base) == 6:
        return f"{hex(int(opacity * 256))[2:].upper()}{base}"

    raise ValueError(f"Color must be either RGB or RRGGBB, got: {base}")

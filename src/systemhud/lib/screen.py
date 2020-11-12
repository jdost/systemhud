from pathlib import Path

MAX_BRIGHTNESS = 50000


class Backlight:
    def __init__(
        self,
        name: str = "intel_backlight",
        max_brightness: int = MAX_BRIGHTNESS,
    ):
        self.name = name
        self.max_brightness = max_brightness
        self.level_file = Path(f"/sys/class/backlight/{name}/brightness")

    @property
    def level(self) -> int:
        return int(self.level_file.read_text())

    @property
    def rlevel(self) -> int:
        return int(self.level / self.max_brightness * 100)

    def set(self, l: int) -> None:
        self.level_file.write_text(str(l))

    def rset(self, l: int) -> None:
        self.set(int(l / 100 * self.max_brightness))

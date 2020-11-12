"""
Wrappers to give pulseaudio information a python interface
"""
import enum
import subprocess
from typing import Optional


class Type(enum.Enum):
    SOURCE = "source"
    SINK = "sink"


class Device:
    device_id: str

    def __init__(self, mixer_type: Type):
        self.device_type = mixer_type
        self.update()

    def update(self) -> None:
        if self.device_type is Type.SOURCE:
            cmd = ["pulsemixer", "--list-sources"]
        else:
            cmd = ["pulsemixer", "--list-sinks"]

        pulsemixer_raw = subprocess.run(
            cmd, stdout=subprocess.PIPE
        ).stdout.decode("utf-8")

        for line in pulsemixer_raw.split("\n"):
            try:
                _, info = line.split(":", 1)
                _, default = info.rsplit(",", 1)
                if default.strip() != "Default":
                    continue
            except ValueError:
                continue

            for kv_pair in info.strip().split(","):
                try:
                    k, v = kv_pair.split(":", 1)
                except ValueError:
                    continue

                if k.strip() not in ["ID", "Name"]:
                    continue

                if k == "ID":
                    self.device_id = v.strip()
                elif k.strip() == "Name":
                    self.name = v.strip()

    @property
    def volume(self) -> int:
        if self.mute:
            return 0

        raw_volume = subprocess.run(
            ["pulsemixer", "--id", self.device_id, "--get-volume"],
            stdout=subprocess.PIPE,
        ).stdout.decode("utf-8")
        l, r = raw_volume.split(" ", 1)
        return int((int(l) + int(r)) / 2)

    @volume.setter
    def volume(self, v: int) -> None:
        subprocess.run(
            [
                "pulsemixer",
                "--id",
                self.device_id,
                "--set-volume",
                str(v),
            ],
            stdout=subprocess.PIPE,
        )

    @property
    def mute(self) -> bool:
        return bool(
            int(
                subprocess.run(
                    ["pulsemixer", "--id", self.device_id, "--get-mute"],
                    stdout=subprocess.PIPE,
                )
                .stdout.decode("utf-8")
                .strip()
            )
        )

    @mute.setter
    def mute(self, v: bool) -> None:
        subprocess.run(
            [
                "pulsemixer",
                "--id",
                self.device_id,
                "--mute" if v else "--un-mute",
            ],
            stdout=subprocess.PIPE,
        )

"""
Wrappers to give pulseaudio information a python interface
"""
import asyncio
import enum
from typing import Optional

from systemhud.util import capture, run


class Type(enum.Enum):
    SOURCE = "source"
    SINK = "sink"


class Device:
    device_id: str

    def __init__(self, mixer_type: Type):
        self.device_type = mixer_type

    async def update(self) -> None:
        if self.device_type is Type.SOURCE:
            cmd = "pulsemixer --list-sources"
        else:
            cmd = "pulsemixer --list-sinks"

        for line in await capture(cmd):
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
    async def volume(self) -> int:
        if await self.mute:
            return 0

        raw_volume = await capture(
            f"pulsemixer --id {self.device_id} --get-volume", split=False
        )
        l, r = raw_volume.split(" ", 1)
        return int((int(l) + int(r)) / 2)

    @volume.setter
    async def volume(self, v: int) -> None:
        await run(f"pulsemixer --id {self.device_id} --set-volume {v}")

    @property
    async def mute(self) -> bool:
        return bool(
            int(
                await capture(
                    f"pulsemixer --id {self.device_id} --get-mute", split=False
                )
            )
        )

    @mute.setter
    async def mute(self, v: bool) -> None:
        flag = "mute" if v else "un-mute"
        await run(f"pulsemixer --id {self.device_id} --{flag}")

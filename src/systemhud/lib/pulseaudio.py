"""
Wrappers to give pulseaudio information a python interface
"""
import re
from typing import AsyncIterator, Dict, List, Optional, Set, Tuple, Union

from systemhud.streams import capture, run
from systemhud.util import ReversableEnum

SUBSCRIBE_REGEX = re.compile(
    r"^Event '(new|change|remove)' on "
    r"(client|sink|sink-input|source|source-output) #([0-9]+)$"
)


class Type(ReversableEnum):
    SOURCE = "source"
    SINK = "sink"


class Event(ReversableEnum):
    NEW = "new"
    REMOVE = "remove"
    CHANGE = "change"


class Device:
    device_id: int
    name: str
    NAME_METADATA_KEY = "properties.device.description"
    _volume: float
    _base: int
    muted: bool

    def __init__(self, mixer_type: Type, device_id: int):
        self.device_type = mixer_type
        self.device_id = device_id
        self.name = ""
        self._volume = -1.0
        self._base = 0
        self.muted = False

    def update(self, metadata: Dict[str, Union[bool, int, str]]) -> None:
        if self.NAME_METADATA_KEY in metadata:
            name = metadata[self.NAME_METADATA_KEY]
            assert isinstance(name, str)
            self.name = name

        if "volume" in metadata:
            assert isinstance(metadata["volume"], str)
            channel_percs: List[int] = []
            for channel in metadata["volume"].split(","):
                _, v = channel.strip().split(":", 1)
                parts = v.strip().split("/")
                perc = parts[1]
                channel_percs.append(int(perc.rstrip("% ")))

            self._volume = sum(channel_percs) / len(channel_percs)

        if "muted" in metadata:
            assert isinstance(metadata["muted"], str)
            self.muted = metadata["muted"] == "yes"

        if "base volume" in metadata:
            assert isinstance(metadata["base volume"], str)
            bv, _ = metadata["base volume"].split("/", 1)
            self._base = int(bv)

    @property
    def volume(self) -> float:
        return 0.0 if self.muted else self._volume

    async def set_volume(self, percv: float) -> None:
        if percv < 0:
            percv = 0.0

        await run(
            f"pacmd set-{self.device_type}-volume {self.device_id} "
            f"{int(self._base * percv / 100)}"
        )

    async def toggle_mute(self) -> None:
        s = 0 if self.muted else 1
        await run(f"pacmd set-{self.device_type}-mute {self.device_id} {s}")

    async def set_default(self) -> None:
        await run(f"pacmd set-default-{self.device_type} {self.device_id}")

    def __repr__(self) -> str:
        return (
            f"<Device ({self.device_type}-{self.device_id}):"
            f" {self.name} - {self.volume}>"
        )


class Devices:
    _default: int
    devices: Dict[int, Device]
    device_type: Type

    def __init__(self, device_type: Type):
        self.device_type = device_type
        self.devices = {}
        self._default = -1

    async def update(self) -> None:
        found_ids: Set[int] = set()
        async for device_metadata in get_devices(self.device_type):
            assert isinstance(device_metadata["id"], int)
            device_id = device_metadata["id"]
            found_ids.add(device_id)

            if device_metadata["default"]:
                self._default = device_id

            self.devices[device_id] = Device(self.device_type, device_id)
            self.devices[device_id].update(device_metadata)

        if set(self.devices) - found_ids:
            deleted_ids = set(self.devices) - found_ids
            for deleted_id in list(deleted_ids):
                del self.devices[deleted_id]

    @property
    def default(self) -> Device:
        return self.devices[self._default]


async def get_devices(
    t: Type,
) -> AsyncIterator[Dict[str, Union[str, int, bool]]]:
    """An attempt at converting the mess of pulseaudio output into something
    usable.  This is *very* likely to be flakey, I hope they add JSON output
    in the future.
    """
    curr: Dict[str, Union[str, int, bool]] = {}
    list_type = "list-sinks" if t is Type.SINK else "list-sources"
    stack: List[str] = []
    for line in await capture(f"pacmd {list_type}", strip=False):
        if not line:
            continue

        if not line.startswith("\t" * len(stack)):
            stack.pop()

        if not stack or "index" in line:
            # These are top level lines, we want to handle the special
            if "index" not in line:
                # This is usually the available count line
                continue

            if curr:
                yield curr

            _, index = line.split(":")

            curr = {
                "id": int(index),
                "default": line.lstrip().startswith("*"),
            }
            stack = [index]
            continue

        line = line.strip()
        if "=" in line:
            k, v = line.split("=", 1)
            v = v.strip('" ')
        elif ":" in line:
            if line.endswith(":"):
                # Sometimes there is just a key prefixing a subset
                k = line[:-1]
                stack.append(k)
                continue

            k, v = line.split(":", 1)
        else:
            continue

        curr[".".join(stack[1:] + [k.strip()])] = v.strip()

    yield curr


def parse_event(line: str) -> Tuple[Optional[Event], Optional[Type], int]:
    match = SUBSCRIBE_REGEX.match(line)
    if not match:
        return None, None, -1

    return (
        Event.rlookup(match.groups()[0]),
        Type.rlookup(match.groups()[1]),
        int(match.groups()[2]),
    )

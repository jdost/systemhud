import asyncio
from typing import Dict, Optional, Tuple, Union

from systemhud.util import ReversableEnum, capture, run, strip_ansi


class BluetoothCtlStatus(ReversableEnum):
    STARTED_PAIRING = "NEW"
    STOPPED_PAIRING = "DEL"
    CHANGED = "CHG"

    @classmethod
    def rlookup(cls, raw: str) -> Optional["BluetoothCtlStatus"]:
        return super().rlookup(raw.strip("[]"))


class BluetoothType(ReversableEnum):
    DEVICE = "Device"
    CONTROLLER = "Controller"


class Device:
    # For some reason, my bluetooth headphones identify as an audio card, which
    # is kind of annoying from a UI perspective, so add in a translation table
    # for these problematic icon identifiers
    ICONS_TRANS = {
        "audio-card": "audio-headphones",
    }
    device_id: str
    name: str
    _icon: str
    connected: bool = False

    def __init__(self, device_id: str):
        self.device_id = device_id
        self.name = ""
        self.connected = False
        self._icon = ""

    async def _get_info(self) -> None:
        for line in await capture(f"bluetoothctl info {self.device_id}"):
            line = line.strip()
            try:
                k, v = line.split(":", 1)
            except ValueError:
                continue

            if k in ["Name", "Alias"]:
                self.name = v.strip()
            elif k == "Connected":
                self.connected = v.strip() == "yes"
            elif k == "Icon":
                self._icon = v.strip()

    @property
    def icon(self) -> str:
        return self.ICONS_TRANS.get(self._icon, self._icon)

    async def update(self) -> bool:
        """Update the info for this device, if the connection status changed,
        will return True."""
        previous_status = self.connected
        await self._get_info()
        return self.connected != previous_status

    async def connect(self) -> None:
        if self.connected:
            return

        await run(f"bluetoothctl connect {self.device_id}")

    async def disconnect(self) -> None:
        if not self.connected:
            return

        await run(f"bluetoothctl disconnect {self.device_id}")

    async def toggle(self) -> None:
        await self.disconnect() if self.connected else await self.connect()

    def __repr__(self) -> str:
        return (
            f"<BluetoothDevice({self.device_id}): {self.name} icon:{self.icon}>"
        )


async def get_devices() -> Dict[str, Device]:
    dev_list = await capture("bluetoothctl paired-devices")

    devices: Dict[str, Device] = {}

    for line in dev_list:
        try:
            _, dev_id, _ = line.split(" ", 2)
        except ValueError:
            continue

        devices[dev_id] = Device(dev_id)
        await devices[dev_id].update()

    return devices


async def get_status() -> bool:
    ctrlr_status = await capture("bluetoothctl show")
    for line in ctrlr_status:
        try:
            k, v = line.strip().split(":", 1)
        except ValueError:
            continue

        if k == "Powered":
            return v.strip() != "no"

    return False


async def toggle() -> None:
    if await get_status():
        await run("bluetoothctl power off")
    else:
        await run("bluetoothctl power on")


def parse_bluetoothctl_logline(
    raw_msg: str,
) -> Tuple[Optional[BluetoothCtlStatus], Optional[BluetoothType], str, str]:
    raw_line = raw_msg.split("\r")[-1]
    line = strip_ansi(raw_line)
    if not line.startswith("["):
        return None, None, "", ""

    try:
        raw_status, raw_type, dev_id, misc = line.split(" ", 3)
    except ValueError:
        return None, None, "", ""

    status = BluetoothCtlStatus.rlookup(raw_status)
    dev_type = BluetoothType.rlookup(raw_type)

    return status, dev_type, dev_id, misc

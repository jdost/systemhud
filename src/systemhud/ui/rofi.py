import asyncio
import shutil
from typing import Dict, List, Optional, Sequence

from systemhud import PKG_ROOT

ROFI_BIN = shutil.which("rofi")


class Entry:
    def __init__(
        self,
        name: str,
        icon: Optional[str] = None,
        urgent: bool = False,
        active: bool = False,
        value: Optional[str] = None,
    ):
        self.name = name
        self.icon = icon
        self.is_urgent = urgent
        self.is_active = active
        self.value = value

    def __str__(self) -> str:
        out = self.name
        if self.icon:
            out += f"\x00icon\x1f{self.icon}"

        return out

    def __repr__(self) -> str:
        meta = ""
        if self.icon:
            meta += f" icon:{self.icon}"
        if self.is_urgent:
            meta += " urgent"
        if self.is_active:
            meta += " active"
        return f"<Entry: {self.name}{meta}>"


async def rofi(
    entries: Sequence[Entry],
    message: str = "",
    theme: str = "icons",
) -> Optional[Entry]:
    assert ROFI_BIN is not None, "rofi is not installed."

    urgents: List[str] = []
    actives: List[str] = []
    items: List[str] = []
    lookup: Dict[str, Entry] = {}

    for i, entry in enumerate(entries):
        if entry.is_urgent:
            urgents.append(str(i))
        if entry.is_active:
            actives.append(str(i))

        items.append(str(entry))
        lookup[entry.name] = entry

    args = [
        "-no-config",
        "-dmenu",
        "-theme",
        str(PKG_ROOT / f"rofi/{theme}.rasi"),
    ]
    args += ["-u", ",".join(urgents)] if urgents else []
    args += ["-a", ",".join(actives)] if actives else []
    args += ["-mesg", message] if message else []
    if theme == "icons":
        args += ["-columns", str(len(entries))]
        args += ["-width", str(len(items) * 5 + 2)]
    else:
        args += ["-lines", str(len(items))]

    rofi_proc = await asyncio.create_subprocess_exec(
        ROFI_BIN,
        *args,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
    )

    stdout, _ = await rofi_proc.communicate("\n".join(items).encode("utf-8"))
    if rofi_proc.returncode != 0:
        return None

    return lookup[stdout.decode().strip()]

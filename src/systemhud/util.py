import enum
import re
import sys
from os import getpid, getuid
from pathlib import Path
from typing import Optional, Type, TypeVar

ANSI_STRIP = re.compile(r"(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]")
NONPRINTABLE_STRIP = re.compile(r"(\x01|\x02)")

T = TypeVar("T", bound="ReversableEnum")


def set_pidfile(name: str) -> None:
    if sys.stdin.isatty():  # Don't set the pidfile if running interactively
        return

    with Path(f"/run/user/{getuid()}/{name}.pid").open("w") as pidfile:
        pidfile.write(str(getpid()))


def strip_ansi(src: str) -> str:
    for f in [ANSI_STRIP, NONPRINTABLE_STRIP]:
        src = f.sub("", src)

    return src


class ReversableEnum(enum.Enum):
    @classmethod
    def rlookup(cls: Type[T], src: str) -> Optional[T]:
        for i in cls:
            if i.value == src:
                return i

        return None

    def __str__(self) -> str:
        return self.value

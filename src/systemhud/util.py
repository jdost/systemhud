import asyncio
import enum
import re
import shlex
import shutil
import sys
from os import getpid, getuid
from pathlib import Path
from typing import (
    AsyncGenerator,
    Literal,
    Optional,
    Sequence,
    Type,
    TypeVar,
    Union,
    overload,
)

from systemhud.errors import ExecutableNotFound

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


@overload
async def capture(full_cmd: str) -> Sequence[str]:
    ...


@overload
async def capture(full_cmd: str, split: Literal[True]) -> Sequence[str]:
    ...


@overload
async def capture(full_cmd: str, split: Literal[False]) -> str:
    ...


async def capture(
    full_cmd: str, split: bool = True
) -> Union[str, Sequence[str]]:
    cmd = shlex.split(full_cmd)
    binary = shutil.which(cmd[0])
    if binary is None:
        raise ExecutableNotFound(cmd[0])

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, _ = await proc.communicate()
    assert proc.returncode == 0, f"Failed: {full_cmd} ({proc.returncode})"

    return stdout.decode() if not split else stdout.decode().split("\n")


async def run(full_cmd: str) -> bool:
    cmd = shlex.split(full_cmd)
    binary = shutil.which(cmd[0])
    if binary is None:
        raise ExecutableNotFound(cmd[0])

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )

    return proc.returncode == 0

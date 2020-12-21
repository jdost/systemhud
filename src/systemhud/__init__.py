import asyncio
import shlex
import shutil
from pathlib import Path
from typing import AsyncGenerator, Awaitable, Callable, List

from systemhud.errors import ExecutableNotFound

PKG_ROOT = list(Path(__file__).resolve().parents)[2]


async def timed_updates(
    update: Callable[[], Awaitable[None]], period: int = 5
) -> None:
    async def _timed_updates():
        while True:
            await update()
            await asyncio.sleep(period)

    await _timed_updates()


async def update_stream(full_cmd: str) -> AsyncGenerator[str, None]:
    cmd = shlex.split(full_cmd)
    binary = shutil.which(cmd[0])
    if binary is None:
        raise ExecutableNotFound(cmd[0])

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    assert proc.stdout is not None

    try:
        while True:
            line = await proc.stdout.readline()
            if not line:
                break

            yield line.decode("utf-8").strip()
    except KeyboardInterrupt:
        proc.kill()


def async_updater(handler: Callable[[], Awaitable[None]]) -> None:
    try:
        asyncio.run(handler())
    except KeyboardInterrupt:
        pass


def register_signal(
    signal: int, handler: Callable[[], Awaitable[None]]
) -> None:
    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal, lambda: asyncio.create_task(handler()))


def run(runner: Callable[[], Awaitable[None]]) -> None:
    asyncio.run(runner())

import asyncio
import atexit
import shlex
import shutil
from pathlib import Path
from typing import AsyncGenerator, Awaitable, Callable, List

from systemhud.errors import ExecutableNotFound
from systemhud.util import start, stream

PKG_ROOT = list(Path(__file__).resolve().parents)[2]
_streams: List[asyncio.subprocess.Process] = []


def _stream_cleaner() -> None:
    """atexit stream terminator
    We spawn indefinite subprocess streams that like to hang around after this
    process restarts, so this attempts to terminate all those still running
    when the process closes (hopefully)
    """
    for stream in _streams:
        if stream.returncode is not None:
            continue
        stream.terminate()


atexit.register(_stream_cleaner)


async def timed_updates(
    update: Callable[[], Awaitable[None]], period: int = 5
) -> None:
    async def _timed_updates():
        while True:
            await update()
            await asyncio.sleep(period)

    await _timed_updates()


async def update_stream(full_cmd: str) -> AsyncGenerator[str, None]:
    proc = await start(full_cmd, pipe=True)
    _streams.append(proc)
    return stream(proc)


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
    try:
        asyncio.run(runner())
    except KeyboardInterrupt:
        pass

import asyncio
import shlex
import shutil
import sys
from typing import AsyncIterator, List, Sequence, Union

from systemhud.errors import ExecutableNotFound

SUDO_CMD = "sudo"
CmdType = Union[str, Sequence[str]]


class Stream:
    _subprocs: List[asyncio.subprocess.Process] = []

    def __init__(self, cmd: CmdType):
        self.full_cmd = shlex.split(cmd) if isinstance(cmd, str) else cmd
        self.proc: Union[None, asyncio.subprocess.Process] = None

    async def start(self, pipe: bool = False) -> asyncio.subprocess.Process:
        if shutil.which(self.full_cmd[0]) is None:
            raise ExecutableNotFound(self.full_cmd[0])

        self.proc = await asyncio.create_subprocess_exec(
            *self.full_cmd,
            stdout=(
                asyncio.subprocess.PIPE if pipe else asyncio.subprocess.DEVNULL
            ),
            stderr=asyncio.subprocess.DEVNULL,
        )
        self.__class__._subprocs.append(self.proc)
        return self.proc

    @classmethod
    def cleanup_all(cls) -> None:
        for subproc in cls._subprocs:
            if subproc.returncode is not None:
                continue
            subproc.terminate()

    def cleanup(self) -> None:
        if self.proc is not None and self.proc.returncode is None:
            self.proc.terminate()

    async def run(self) -> bool:
        await self.start()
        assert self.proc is not None
        await self.proc.wait()
        return self.proc.returncode == 0

    async def capture(self, strip: bool = True) -> List[str]:
        output: List[str] = []
        async for line in self:
            output.append(line.strip() if strip else line)

        return output

    def __aiter__(self) -> AsyncIterator[str]:
        return self

    async def __anext__(self) -> str:
        if self.proc is None:
            await self.start(pipe=True)
        assert self.proc is not None
        assert self.proc.stdout is not None

        line = await self.proc.stdout.readline()
        if not line:
            raise StopAsyncIteration

        return line.decode("utf-8")


async def capture(cmd: CmdType, strip: bool = True) -> List[str]:
    return await Stream(cmd).capture(strip=strip)


async def run(cmd: CmdType, as_root: bool = False) -> bool:
    if as_root:
        if isinstance(cmd, str):
            return await Stream(f"{SUDO_CMD} " + cmd).run()
        else:
            return await Stream([SUDO_CMD, *cmd]).run()
    return await Stream(cmd).run()

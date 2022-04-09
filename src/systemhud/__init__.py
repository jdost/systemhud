import asyncio
import signal
import time
from enum import IntEnum
from pathlib import Path
from sys import stdout
from typing import Awaitable, Callable, Dict, List, Optional, Set, Union

from systemhud.streams import Stream
from systemhud.ui.icons import BaseIcon

PKG_ROOT = list(Path(__file__).resolve().parents)[2]


class InteractionType(IntEnum):
    LEFT_CLICK = signal.SIGUSR1
    RIGHT_CLICK = signal.SIGUSR2


class Applet:
    READINESS_DELAY = 2

    def __init__(self, name: str):
        self.name = name
        self._updaters: Set[Callable[[], Awaitable[None]]] = set()
        self._setup_hooks: Set[Callable[[], Awaitable[bool]]] = set()
        self._interaction_handlers: Dict[
            int, Callable[[], Awaitable[None]]
        ] = {}
        self._pending_tasks: List[asyncio.Task] = []

    def setup(
        self, setup_func: Callable[[], Awaitable[None]]
    ) -> Callable[[], Awaitable[bool]]:
        # We register a setup as a readiness that runs once and then signals it
        #  is ready
        async def wrapped_hook_func() -> bool:
            await setup_func()
            return True

        self._setup_hooks.add(wrapped_hook_func)
        return wrapped_hook_func

    def readiness(
        self, readiness_func: Callable[[], Awaitable[bool]]
    ) -> Callable[[], Awaitable[bool]]:
        self._setup_hooks.add(readiness_func)
        return readiness_func

    def make_launcher(
        self, runner: Callable[[], Awaitable[None]]
    ) -> Callable[[], None]:
        def launcher() -> None:
            self._pending_tasks.append(asyncio.create_task(runner()))

        return launcher

    def timed_update(
        self, period: int
    ) -> Callable[
        [Callable[[], Awaitable[Optional[BaseIcon]]]], Callable[[], None]
    ]:
        def wrapped_update_handler(
            f: Callable[[], Awaitable[Optional[BaseIcon]]]
        ) -> Callable[[], None]:
            async def timed_update_runner() -> None:
                while True:
                    self.print_icon(await f())
                    await asyncio.sleep(period)

            self._updaters.add(timed_update_runner)
            return self.make_launcher(timed_update_runner)

        return wrapped_update_handler

    def stream_update(
        self, input_stream: Union[str, Stream]
    ) -> Callable[
        [Callable[[str], Awaitable[Optional[BaseIcon]]]], Callable[[], None]
    ]:
        def wrapped_stream_handler(
            f: Callable[[str], Awaitable[Optional[BaseIcon]]]
        ) -> Callable[[], None]:
            async def stream_update_runner() -> None:
                async for line in (
                    Stream(input_stream)
                    if isinstance(input_stream, str)
                    else input_stream
                ):
                    self.print_icon(await f(line.strip()))

            self._updaters.add(stream_update_runner)
            return self.make_launcher(stream_update_runner)

        return wrapped_stream_handler

    def interaction(
        self, trigger: InteractionType
    ) -> Callable[[Callable[[], Awaitable[None]]], Callable[[], None]]:
        def wrapped_interaction_handler(f: Callable[[], Awaitable[None]]):
            self._interaction_handlers[trigger.value] = f
            return self.make_launcher(f)

        return wrapped_interaction_handler

    def run(self) -> None:
        asyncio.run(self._run())

    def print_icon(self, icon: Union[None, BaseIcon, str]) -> None:
        if not icon:
            return

        print(icon)
        stdout.flush()

    async def wait_for_tasks(self) -> None:
        finished_tasks = 0
        while len(self._pending_tasks) > finished_tasks:
            finished_tasks = 0
            for pending_task in self._pending_tasks:
                if pending_task.done():
                    finished_tasks += 1
                    pending_task.result()
            await asyncio.sleep(2)

    async def cleanup(self) -> None:
        cancelled_tasks: List[asyncio.Task] = []
        loop = asyncio.get_running_loop()
        for task in asyncio.all_tasks(loop):
            if not task.done():
                cancelled_tasks.append(task)
                task.cancel()

        for task in cancelled_tasks:
            try:
                await task
            except asyncio.CancelledError:
                pass

        Stream.cleanup_all()

    async def _run(self) -> None:
        loop = asyncio.get_running_loop()

        setup_hooks = self._setup_hooks
        while setup_hooks:
            unfinished_hooks = set()
            for hook in setup_hooks:
                if not await hook():
                    unfinished_hooks.add(hook)

            setup_hooks = unfinished_hooks
            if setup_hooks:  # Don't sleep if all hooks finished cleanly
                time.sleep(self.READINESS_DELAY)

        for signal, handler in self._interaction_handlers.items():
            loop.add_signal_handler(
                signal, lambda: asyncio.create_task(handler())
            )

        self._pending_tasks = [asyncio.create_task(u()) for u in self._updaters]
        try:
            await self.wait_for_tasks()
        except Exception:
            await self.cleanup()
            raise

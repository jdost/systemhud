from time import sleep
from typing import Callable


def timed_updates(update: Callable[[], None], period: int = 5) -> None:
    while True:
        update()
        sleep(period)

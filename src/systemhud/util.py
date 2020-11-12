import sys
from os import getpid, getuid
from pathlib import Path


def set_pidfile(name: str) -> None:
    if sys.stdin.isatty():  # Don't set the pidfile if running interactively
        return

    with Path(f"/run/user/{getuid()}/{name}.pid").open("w") as pidfile:
        pidfile.write(str(getpid()))

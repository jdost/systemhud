import hashlib
import shutil
import urllib.request as urllib
from asyncio.subprocess import Process
from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator, NamedTuple, Optional, Tuple

from systemhud.util import ReversableEnum, capture, start, stream

STATUS_STREAM_CMD = (
    "/usr/bin/playerctl -a -F metadata -f '{{lc(status)}}\1{{playerName}}'"
)
MPRIS_PLAYER_METADATA_FORMAT = (
    "{{artist}}\1{{album}}\1{{title}}\1{{mpris:artUrl}}"
)


class Status(ReversableEnum):
    PLAYING = "playing"
    PAUSED = "paused"
    UNKNOWN = "<unknown>"


class Track(NamedTuple):
    artist: Optional[str]
    title: str
    album: Optional[str]
    art: Optional[str]

    def __str__(self) -> str:
        if self.artist == "None":
            return self.title

        return f"{self.artist} - {self.title}"


class Player:
    proc: Optional[Process]

    def __init__(self, name: str, status: Status):
        self.name = name
        self._status = status
        self.proc = None
        self.last_updated = datetime.now()

    def is_active(self) -> bool:
        return self.status is Status.PLAYING

    @property
    def status_cmd(self) -> str:
        return (
            f"/usr/bin/playerctl --player={self.name} -F metadata "
            f"-f '{MPRIS_PLAYER_METADATA_FORMAT}'"
        )

    async def refresh_status(self) -> Status:
        new_status = Status.rlookup(
            await capture(
                f"/usr/bin/playerctl --player={self.name} status", split=False
            )
        )
        assert isinstance(new_status, Status)
        self._status = new_status
        return self.status

    @property
    def status(self) -> Status:
        return self._status

    def stop(self) -> None:
        if self.proc is not None and self.proc.returncode is None:
            self.proc.terminate()

    async def status_stream(self) -> AsyncGenerator[Optional[Track], None]:
        self.proc = await start(self.status_cmd, pipe=True)
        async for line in stream(self.proc):
            print(f"{self.name}: {line!r}")
            if not line:
                await self.refresh_status()
                print(f"refreshing status: {self.name} - {self.status}")
            yield parse_track_logline(line)

    def update(self, status: Status) -> bool:
        if status is self._status:
            return False

        self._status = status
        self.last_updated = datetime.now()
        return True

    def __repr__(self) -> str:
        return f"<Player[{self.name}] {self.status.value}>"


def parse_status_logline(raw_msg: str) -> Tuple[str, Optional[Status]]:
    try:
        raw_status, name = raw_msg.split("\1")
        return name, Status.rlookup(raw_status)
    except ValueError:
        return "", None


def parse_track_logline(raw_msg: str) -> Optional[Track]:
    if "\1" not in raw_msg:
        return None

    artist, album, title, art = raw_msg.split("\1", 3)
    return Track(
        artist=None if not artist else artist,
        title=title,
        album=None if not album else album,
        art=None if not art else art,
    )


def get_album_art(url: str) -> Path:
    img_hash = hashlib.sha256(url.encode()).hexdigest()
    img = Path(f"/tmp/albumart/{img_hash}")

    if img.exists():
        return img

    if not img.parent.is_dir():
        img.parent.mkdir()

    img.touch()
    with img.open("wb") as f, urllib.urlopen(url) as img_request:
        shutil.copyfileobj(img_request, f)

    return img

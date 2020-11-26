from os import getuid
from pathlib import Path
from typing import Any, Optional


def progress_bar(n: int, width: int = 20, color: str = "33CC33") -> str:
    bar = (
        "<span font_desc='monospace' size='large'>"
        f"<span background='#{color}'>"
    )
    step_size = int(100 / width)
    progress = n
    for i in range(width):
        if progress <= 0 and progress > step_size * -1:
            bar += "</span><span background='#666666'>"

        bar += " "
        progress -= step_size

    bar += "</span></span>\n"
    return bar


class Notification:
    def __init__(
        self,
        name: str = "polybar",
        icon: Optional[str] = None,
        transient: bool = False,
        timeout: int = 4000,
    ):
        self.name = name
        self.icon = icon
        self._transient = transient
        self._notification_ref = None
        self._timeout = timeout

    @property
    def ref(self) -> Any:
        if not self._notification_ref:
            import gi

            gi.require_version("Notify", "0.7")
            from gi.repository import Notify

            Notify.init(self.name)

            self._notification_ref = Notify.Notification.new("", "", "")
            self._set_transient()

        return self._notification_ref

    @property
    def timeout(self) -> int:
        return self._timeout

    @timeout.setter
    def timeout(self, v: int) -> None:
        self._timeout = v
        self._set_timeout()

    def _set_timeout(self) -> None:
        if not self._notification_ref:
            return

        self._notification_ref.set_timeout(self._timeout)

    @property
    def transient(self) -> bool:
        return self._transient

    @transient.setter
    def transient(self, v: bool) -> None:
        self._transient = v
        self._set_transient()

    def _set_transient(self) -> None:
        if not self._notification_ref:
            return

        from gi.repository import GLib

        self._notification_ref.set_hint(
            "transient", GLib.Variant("b", self._transient)
        )

    def __call__(
        self,
        title: str,
        body: str,
        icon: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        timeout = timeout or self.timeout
        icon = icon or self.icon
        self.ref.update(title, body, icon)
        self.timeout = timeout
        self.ref.show()


class TrackedNotification(Notification):
    def __init__(self, name: str):
        self.id_file = Path(f"/var/run/user/{getuid()}/notifications/{name}.id")
        if not self.id_file.parent.is_dir():
            self.id_file.parent.mkdir(parents=True)

        super().__init__(name)

    def __call__(
        self,
        title: str,
        body: str,
        icon: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> None:
        if self.id_file.exists():
            self.ref.set_property("id", int(self.id_file.read_text()))
        else:
            self.id_file.touch()

        super().__call__(title, body, icon, timeout)
        self.id_file.write_text(str(self.ref.props.id))

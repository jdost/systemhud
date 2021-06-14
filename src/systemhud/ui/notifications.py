from os import getuid
from pathlib import Path
from typing import Any, Dict, Optional


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
        hints: Optional[Dict[str, Any]] = None,
    ):
        self.name = name
        self.icon = icon
        self._transient = transient
        self._notification_ref = None
        self._timeout = timeout
        self.hints = hints if hints else {}

    @property
    def ref(self) -> Any:
        if not self._notification_ref:
            import gi

            gi.require_version("Notify", "0.7")
            from gi.repository import Notify

            Notify.init(self.name)

            self._notification_ref = Notify.Notification.new("", "", "")
            self._set_transient()
            self._set_hints()

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

    def _set_transient(self) -> None:
        if not self._notification_ref:
            return

        if not self._transient:
            return

        from gi.repository import GLib

        self._notification_ref.set_hint(
            "transient", GLib.Variant("i", self._transient)
        )

    def _set_hints(self) -> None:
        if not self._notification_ref:
            return

        _hint_type_lookup = {bool: "b", float: "d", int: "i", str: "s"}

        from gi.repository import GLib

        for k, v in self.hints.items():
            type_str = _hint_type_lookup.get(type(v))
            if not type_str:
                continue

            self._notification_ref.set_hint(k, GLib.Variant(type_str, v))

    def _set_image(self, i: str) -> None:
        if not self._notification_ref:
            return

        from gi.repository import GLib

        self._notification_ref.set_hint("image-path", GLib.Variant("s", i))

    def _set_progress(self, l: int) -> None:
        if not self._notification_ref:
            return

        from gi.repository import GLib

        self._notification_ref.set_hint("value", GLib.Variant("i", l))

    def __call__(
        self,
        title: str,
        body: str,
        icon: Optional[str] = None,
        timeout: Optional[int] = None,
        image: Optional[str] = None,
        transient: Optional[bool] = None,
        progress: Optional[int] = None,
    ):
        timeout = timeout or self.timeout
        icon = icon or self.icon
        self.ref.update(title, body, icon)
        if image:
            self._set_image(image)
        if progress:
            self._set_progress(progress)
        if transient is not None and transient != self._transient:
            self._transient = transient
            self._set_transient()
        self.timeout = timeout
        self.ref.show()


class TrackedNotification(Notification):
    def __init__(self, name: str, **kwargs: Any):
        self.id_file = Path(f"/var/run/user/{getuid()}/notifications/{name}.id")
        if not self.id_file.parent.is_dir():
            self.id_file.parent.mkdir(parents=True)

        super().__init__(name, **kwargs)

    def __call__(
        self,
        title: str,
        body: str,
        icon: Optional[str] = None,
        timeout: Optional[int] = None,
        image: Optional[str] = None,
    ) -> None:
        if self.id_file.exists():
            self.ref.set_property("id", int(self.id_file.read_text()))
        else:
            self.id_file.touch()

        super().__call__(title, body, icon, timeout, image)
        self.id_file.write_text(str(self.ref.props.id))

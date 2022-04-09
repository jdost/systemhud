from typing import Callable, List, Optional

from systemhud.ui import colors

MONOSPACE = "Anonymice Nerd Font Mono"
CLOSE_TAG = "</span>"


def span_tag(
    foreground: Optional[colors.Color] = None,
    background: Optional[colors.Color] = None,
    font: Optional[str] = None,
    size: Optional[int] = None,
    weight: Optional[str] = None,
    underline: Optional[str] = None,
) -> str:
    tag: List[str] = ["span"]
    if foreground:
        tag.append(f"foreground='#{str(foreground)[2:]}'")
    if background:
        tag.append(f"background='#{str(background)[2:]}'")
    if font:
        font_desc = font
        if weight:
            font_desc += f" {weight}"
        if size:
            font_desc += f" {size}"
        tag.append(f"font_desc='{font_desc}'")
    else:
        if size:
            tag.append(f"size='{size}'")
        if weight:
            tag.append(f"weight='{weight}'")
    if underline:
        tag.append(f"underline='{underline}'")

    return f"<{' '.join(tag)}>"


def wrap(contents: str, **props) -> str:
    return span_tag(**props) + contents + CLOSE_TAG


def wrapped(**props) -> Callable[[str], str]:
    def wrapper(contents: str) -> str:
        return wrap(contents, **props)

    return wrapper

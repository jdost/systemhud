from systemhud.ui import colors
from systemhud.ui.icons import GradientIcon, Icon, ProgressiveIcon

AC = Icon("")
BATTERY_LEVELS = ProgressiveIcon("󰂎󰁺󰁻󰁼󰁽󰁾󰁿󰂀󰂁󰂂󰁹")
BLUETOOTH_ = {
    "on": Icon("󰂯"),
    "off": Icon("󰂲", fg=colors.GREY),
    "connected": Icon("󰂱", fg=colors.CYAN),
}
CPU = GradientIcon("")
MEMORY = GradientIcon("")
UNKNOWN = Icon("?")

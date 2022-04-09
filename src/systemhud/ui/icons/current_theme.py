from systemhud.ui.icons import (
    THEME,
    EnumIcon,
    GradientIcon,
    Icon,
    ProgressiveIcon,
)

# Typing for import overloads
AC: Icon
BATTERY_LEVELS: ProgressiveIcon
CPU: GradientIcon
MEMORY: GradientIcon
UNKNOWN: Icon

if THEME.lower() == "fluent":
    from systemhud.ui.icons.fluent import *
elif THEME.lower() == "material" or THEME == "":
    from systemhud.ui.icons.material import *
else:
    raise ValueError(f"{THEME} is not a defined theme.")

# The Enum needs to be defined here, the imported ones are different enums
class BLUETOOTH(EnumIcon):
    on = BLUETOOTH_["on"]
    off = BLUETOOTH_["off"]
    connected = BLUETOOTH_["connected"]

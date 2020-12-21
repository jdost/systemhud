# `systemhud`

Collection of helper definitions that I use to build various HUD elements
for my system.  These interact/are used by various HUD elements like
notification daemons, statusbars, selectors, etc.  The main goal of this
is to centralize useful pieces that assemble into powerful information
displays for my systems.

## Expected Deps

For the polybar icons, I use fonts from the [nerd fonts
project](https://www.nerdfonts.com/), so most of the icons expect stuff in
that unicode space.

For the notifications, I use deadd aka
[linux-notification-center](https://github.com/phuhl/linux_notification_center)
but most of the stuff should work fine for other notification daemons,
even though not all features may work now (or in the future) like
images/icons, pango markup, or buttons.

The dialogs use [rofi](https://github.com/davatorium/rofi) and probably
a pretty recent version (tested using `1.6.1`) so some configs/flags may
not work in older versions.

The pulseaudio applet utilizes `pulsemixer` for the convenience wrappers
instead of trying to parse the output from `pactl`.  The bluetooth applet
uses `bluetoothctl`.  Probably some other things missing...

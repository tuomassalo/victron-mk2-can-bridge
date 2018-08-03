# victron-mk2-can-bridge

With this project, one can use a Rasberry Pi, [USBtin](https://www.fischl.de/usbtin/) and a MK2-USB adapter (Victron ASS030130000) to convert metrics from a Victron MultiPlus inverter to (custom) CAN bus messages.

## Installation

- install `flash` from https://github.com/hypriot/flash

- insert SD card

- run `flash --userdata user-data.yml  https://github.com/hypriot/image-builder-rpi/releases/download/v1.9.0/hypriotos-rpi-v1.9.0.img.zip`

- eject the card

- boot the RPi with a network cable plugged in, wait at least 10 minutes.

- to see logs with `journalctl -f` or `tail -f /var/log/bridge.log`, login with `bridge`/`bridge` (find the IP with e.g. `nmap` or login locally)

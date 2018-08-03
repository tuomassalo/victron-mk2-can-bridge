# victron-mk2-can-bridge
Use a RPi to read Victron inverter data via mk2usb and write it to CAN bus via usbtin.

Installation
============

- install `flash` from https://github.com/hypriot/flash

- insert SD card

- run `flash --userdata user-data.yml  https://github.com/hypriot/image-builder-rpi/releases/download/v1.9.0/hypriotos-rpi-v1.9.0.img.zip`

- eject the card

- boot the RPi with a network cable plugged in, wait at least 10 minutes.

- to see logs with `journalctl -f` or `tail -f /var/log/bridge.log`, login with `bridge`/`bridge` (find the IP with e.g. `nmap` or login locally)

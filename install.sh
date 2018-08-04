#!/bin/bash

# fail on error
set -e

apt-get update
apt-get -y upgrade
apt-get -y install libjson-perl

cd /tmp/

git clone https://github.com/tuomassalo/victron-mk2-can-bridge.git
cd victron-mk2-can-bridge

mv host-scripts /opt/

# The first container launch is slow, because the images are built.
# Do it before starting the watchdog.
# NB: First launch is allowed to fail. We still want to finish this script.
/opt/host-scripts/launch-container.sh || /bin/true

mv cron-entry.txt /etc/cron.d/bridge-watchdog

# Improve boot time for networkless boot
echo -e '\n\ntimeout 10;\nretry 20;' >> /etc/dhcp/dhclient.conf

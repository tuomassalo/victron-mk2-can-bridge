#!/bin/bash

set -e

cd /opt/host-scripts

mkdir -p /opt/shared-dir

docker rm -f $(docker ps -a -q) || /bin/true

docker build -t tuomassalo/rpi-python-victron .
docker run \
	--device=/dev/ttyUSB0 \
	--device=/dev/ttyACM0 \
	--volume /opt/shared-dir:/opt/shared-dir \
	-i tuomassalo/rpi-python-victron \
	/opt/shared-dir/forever.sh

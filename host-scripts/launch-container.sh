#!/bin/bash

set -e

cd /opt/host-scripts

mkdir -p /opt/shared-dir

docker ps|perl -wlane 'print "docker rm -f $F[0]" unless /^CONTAINER.ID/' | sh > /dev/null

docker build -t tuomassalo/rpi-python-victron . &&
docker run \
	--device=/dev/ttyUSB0 \
	--device=/dev/ttyACM0 \
	--volume /opt/shared-dir:/opt/shared-dir \
	-i tuomassalo/rpi-python-victron \
	/opt/shared-dir/forever.sh

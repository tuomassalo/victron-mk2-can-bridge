#!/bin/bash

set -e

SharedDir=/opt/shared-dir
cd /opt/host-scripts

rm -rf $SharedDir/bridge-scripts
cp -r bridge-scripts $SharedDir

docker rm -f $(docker ps -a -q) || /bin/true

docker build -t tuomassalo/rpi-python-victron .
docker run \
	--device=/dev/ttyUSB0 \
	--device=/dev/ttyACM0 \
	--volume $SharedDir:$SharedDir \
	-i tuomassalo/rpi-python-victron \
	$SharedDir/forever.sh

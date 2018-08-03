#!/bin/bash

cd /opt/shared-dir

while true; do
	# unbuffered output
  python -u bridge.py
  sleep 5
done

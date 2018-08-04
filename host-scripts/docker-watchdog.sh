#!/bin/bash

# This is run OUTSIDE of the container

# An attempt to minimize loss on power outage
sync

Logfile="/var/log/bridge.log"
Status=$(
  tail -c 20000 $Logfile |
  grep state_age         |
  tail -n 1              |
  perl -MJSON -wlne '
    $j=JSON::from_json($_);
    print "OK" if(
      $j->{v} > 30
      and abs(time() - $j->{t}        ) < 100
      and $j->{state_age}               < 300
    )'
)

if [[ "$Status" != "OK" ]]; then
  date

  read -d. Seconds < /proc/uptime
  if (( $Seconds < 5*60 )); then
    echo "[UPTIME less than 5 minutes, not restarting.]"
    exit 0
  fi

  echo "RESTARTING..."
  cd /opt/host-scripts && bash launch-container.sh >> $Logfile 2>&1
fi

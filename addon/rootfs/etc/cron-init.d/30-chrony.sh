#!/usr/bin/with-contenv bash

cat <<EOF > /etc/chrony/chrony.conf

pool 127.127.28.0 prefer minpoll 4 maxpoll 4   # GPSD SHM
allow 10.0.0.0/8
allow 192.168.0.0/16

driftfile /var/lib/chrony/drift

makestep 1.0 -1
rtcsync

log tracking measurements statistics

EOF

if [ -e /dev/pps0 ]; then
cat <<EOF >> /etc/chrony/chrony.conf

refclock PPS /dev/pps0 lock GPS refid PPS prefer
EOF
fi

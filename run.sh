#!/bin/bash

# 1. Auto-detect GPS Device
GPS_DEV=$(ls /dev/ttyUSB* /dev/ttyACM* | head -n 1)
if [ -z "$GPS_DEV" ]; then
    echo "No GPS device found. Waiting..."
fi

# Run optimization script
chmod +x /app/scripts/ublox_optimize.sh
/app/scripts/ublox_optimize.sh $GPS_DEV

# 3. Start GPSD with PPS support
# -n: don't wait for client, -n: read from device immediately
gpsd -N -n $GPS_DEV

# 4. Apply Chrony config and start
chronyd -f /app/chrony.conf.template

# 5. Start Python Manager (MQTT & Web UI)
python3 /app/src/main.py

#!/bin/bash

# 1. Parse options from Home Assistant's config file

if [ -f /data/options.json ]; then
    GPS_DEV=$(grep -o '"gps_device": "[^"]*' /data/options.json | cut -d'"' -f4)
else
    GPS_DEV=$(ls /dev/ttyUSB* /dev/ttyACM* | head -n 1)
    if [ -z "$GPS_DEV" ]; then
        echo "No GPS device found. Waiting..."
    fi
fi

# 2. Export options as environment variables so the Python code can see them
export MQTT_HOST=$(grep -o '"mqtt_host": "[^"]*' /data/options.json | cut -d'"' -f4)
export MQTT_USER=$(grep -o '"mqtt_user": "[^"]*' /data/options.json | cut -d'"' -f4)
export MQTT_PASS=$(grep -o '"mqtt_password": "[^"]*' /data/options.json | cut -d'"' -f4)

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

echo "Starting GPS NTP Server with device $GPS_DEV"

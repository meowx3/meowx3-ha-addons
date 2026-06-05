#!/bin/bash

# --- Configuration from HA UI ---
GPS_DEV=${GPS_DEVICE:-"/dev/ttyUSB0"}
PPS_DEV=${PPS_DEVICE:-"/dev/pps0"}
BAUD=${BAUD_RATE:-"9600"}
USE_PPS=${ENABLE_PPS:-"true"}

echo "Starting GPS NTP Server (Debian Edition)..."

# 1. Auto-Detect GPS Device
if [ ! -e "$GPS_DEV" ]; then
    echo "Specified $GPS_DEV not found. Searching..."
    for dev in /dev/ttyUSB* /dev/ttyACM*; do
        if [ -e "$dev" ]; then
            echo "Auto-detected GPS at $dev"
            GPS_DEV=$dev
            break
        fi
    done
fi

# 2. UBLOX Optimization via ubxtool
# Now that python3-gps is installed, this will work!
if command -v ubxtool >/dev/null; then
    echo "Applying UBLOX optimizations to $GPS_DEV..."
    # Example: Enable GNSS constellations (GPS+GLONASS)
    ubxtool -d $GPS_DEV -C CFG-GNSS-CONSTELLATIONS 0x0003
    # Set update rate (1Hz)
    ubxtool -d $GPS_DEV -C CFG-NAV-RATE 1
fi

# 3. Configure Chrony
# Replace PPS placeholder in template
if [ "$USE_PPS" == "true" ]; then
    PPS_CONF="refclock PPS $PPS_DEV poll 0 delay 0.0 precision 1e-4"
else
    PPS_CONF="# PPS Disabled"
fi

sed "s/{{PPS_CONFIG}}/$PPS_CONF/" /etc/chrony.conf.template > /etc/chrony.conf

# 4. Start GPSD
# -n: don't read config file, -s: set speed
gpsd -N -n $GPS_DEV -s $BAUD

# 5. Start Chrony in the foreground
echo "Starting Chronyd..."
chronyd -f

# --- Health Check Loop ---
while true; do
    if gpspipe -w | grep -q "time"; then
        echo "$(date): HEALTH: GPS Fix OK" > /var/log/gpsntp/health.log
    else
        echo "$(date): HEALTH: Searching for satellites..." > /var/log/gpsntp/health.log
    fi
    sleep 60
done &

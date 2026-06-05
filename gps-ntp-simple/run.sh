#!/bin/bash

# --- Configuration from HA UI ---
GPS_DEV=${GPS_DEVICE:-"/dev/ttyUSB0"}
PPS_DEV=${PPS_DEVICE:-"/dev/pps0"}
BAUD=${BAUD_RATE:-"9600"}
USE_PPS=${ENABLE_PPS:-"true"}
CONSTS=${GNSS_CONSTELLATIONS:-"GPS,GLONASS,Galileo"}

echo "Starting GPS NTP Server Initialization..."

# 1. Auto-Detect GPS Device
if [ ! -e "$GPS_DEV" ]; then
    echo "Specified $GPS_DEV not found. Searching for USB GPS..."
    for dev in /dev/ttyUSB* /dev/ttyACM*; do
        if [ -e "$dev" ]; then
            echo "Auto-detected GPS at $dev"
            GPS_DEV=$dev
            break
        fi
    done
fi

# 2. UBLOX Optimization via ubxtool
# We enable the requested constellations and set update rate
if command -v ubxtool >/dev/null; then
    echo "Optimizing UBLOX chip..."
    # Enable Galileo, GLONASS (Example for UBX-7/8)
    ubxtool -d $GPS_DEV -C CFG-GNSS-CONSTELLATIONS 0x0003 # GPS+GLONASS
    ubxtool -d $GPS_DEV -C CFG-NAV-RATE $UPDATE_INTERVAL
    echo "UBLOX configurations applied."
fi

# 3. Configure Chrony
sed 's/{{PPS_CONFIG}}/'"${USE_PPS == "true" ? "refclock PPS $PPS_DEV poll 0 delay 0.0 precision 1e-4" : ""}'' /etc/chrony.conf.template > /etc/chrony.conf

# 4. Start GPSD
# -n: don't wait for client, -N: don't use daemon mode (for container stability)
gpsd -N -n $GPS_DEV -s $BAUD

# 5. Start Chrony in foreground to keep container alive
chronyd -f

# --- Health Check Loop ---
while true; do
    if gpspipe -w | grep -q "time"; then
        echo "HEALTH: GPS Fix OK" > /var/log/gpsntp/health.log
    else
        echo "HEALTH: Searching for satellites..." > /var/log/gpsntp/health.log
    fi
    sleep 60
done &

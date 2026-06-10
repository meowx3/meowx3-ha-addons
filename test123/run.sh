#!/bin/sh

# Get options from config.yaml (passed as env vars by HA)
DEVICE=${DEVICE:-/dev/ttyUSB0}
BAUDRATE=${BAUDRATE:-9600}

echo "Starting gpsd on $DEVICE at $BAUDRATE baud..."

# Start gpsd in the background
gpsd $DEVICE -N -n -b $BAUDRATE

# Echo GPS data to shell using gpspipe
gpspipe -r

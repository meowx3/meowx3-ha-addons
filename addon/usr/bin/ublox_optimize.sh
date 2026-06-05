#!/usr/bin/env bash

DEVICE=$1

# Enable multi-GNSS
ubxtool -f $DEVICE -p CFG-GNSS

# Prefer GPS + Galileo + GLONASS
ubxtool -f $DEVICE -e GPS -e GAL -e GLO

# Improve time pulse stability
ubxtool -f $DEVICE -p CFG-TP5

FROM ghcr.io/home-assistant/amd64-base:latest

RUN apk add --no-cache \
    gpsd gpsd-clients \
    chrony \
    python3 py3-pip \
    mosquitto-clients \
    udev \
    bash \
    socat \
    tzdata \
    build-base

RUN pip install fastapi uvicorn paho-mqtt psutil

COPY rootfs /

RUN chmod +x /etc/services.d/*/run
RUN chmod +x /etc/cont-init.d/*

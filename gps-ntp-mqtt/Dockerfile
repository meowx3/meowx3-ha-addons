FROM alpine:3.18

# Install dependencies
RUN apk add --no-cache \
    gpsd gpsd-clients chrony python3 py3-pip \
    bash gcc musl-dev linux-headers \
    nano util-linux conntrack-tools

# Install Python requirements
RUN pip install paho-mqtt flask psutil

# Copy project files
COPY . /app
WORKDIR /app

# Setup directories for Chrony
RUN mkdir -p /var/lib/chrony

# Expose NTP and Web UI ports
EXPOSE 123/udp 8080

RUN chmod a+x /app/run.sh
CMD ["/app/run.sh"]

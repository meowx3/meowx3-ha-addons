import time, subprocess, json

def restart(service):
    subprocess.call(["s6-svc", "-r", f"/run/service/{service}"])

while True:
    devices = subprocess.getoutput("python3 /usr/bin/gps_detect.py")

    if "/dev/tty" not in devices:
        restart("gpsd")

    time.sleep(10)

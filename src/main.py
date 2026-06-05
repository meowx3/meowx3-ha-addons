import time
import paho.mqtt.client as mqtt
from flask import Flask, jsonify, render_template
import subprocess
import json

# Configuration (Passed from HA via Environment Variables)
MQTT_HOST = "192.168.x.x" 
MQTT_USER = "ha-user"
MQTT_PASS = "password"

app = Flask(__name__)
mqtt_client = mqtt.Client()

def get_gps_data():
    # Query gpsd via cgps or gpspipe
    result = subprocess.check_output(['gpspipe', '-w'], timeout=2)
    return json.loads(result)

def publish_telemetry(data):
    # MQTT Auto-discovery for HA
    payload = {
        "state": data['fix_quality'],
        "sats": data['satellites'],
        "precision": data['precision']
    }
    mqtt_client.publish("homeassistant/sensor/gps_ntp/state", json.dumps(payload), retain=True)

@app.route('/')
def dashboard():
    return render_template('index.html') # See below for UI logic

@app.route('/api/stats')
def stats():
    # Get Chrony status
    chrony_stat = subprocess.check_output(['chronyc', 'tracking']).decode()
    gps_data = get_gps_data()
    return jsonify({"chrony": chrony_stat, "gps": gps_data})

if __name__ == "__main__":
    mqtt_client.connect(MQTT_HOST, 1883, 60)
    mqtt_client.loop_start()
    app.run(host='0.0.0.0', port=8080)

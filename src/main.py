import os
import time
import json
import threading
from flask import Flask, jsonify, render_template
import paho.mqtt.client as mqtt

# Import our Hardware Abstraction Layer
from gps_manager import GPSManager

# --- CONFIGURATION (Loaded from HA Addon Options via Env Vars) ---
MQTT_HOST = os.getenv("MQTT_HOST", "192.168.1.50")
MQTT_USER = os.getenv("MQTT_USER", "homeassistant")
MQTT_PASS = os.getenv("MQTT_PASS", "password")
MQTT_TOPIC_PREFIX = "homeassistant/sensor/gps_ntp"

# Initialize Hardware Manager and Flask App
gps_mgr = GPSManager()
app = Flask(__name__)
mqtt_client = mqtt.Client()

# Global variable to store the latest snapshot for the Web UI to avoid constant hardware polling
latest_snapshot = {}

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT Broker with result code {rc}")
    send_mqtt_discovery()

def send_mqtt_discovery():
    """
    Tells Home Assistant that these entities exist so they appear automatically.
    This implements the HA MQTT Discovery protocol.
    """
    entities = {
        "status": {"name": "GPS NTP Status", "unit": ""},
        "sats": {"name": "Visible Satellites", "unit": "count"},
        "precision": {"name": "Timing Precision", "unit": "ns"},
        "antenna": {"name": "Antenna Quality", "unit": ""},
        "stratum": {"name": "NTP Stratum", "unit": ""}
    }

    for entity_id, info in entities.items():
        config_payload = {
            "name": info["name"],
            "stat_type": "state",
            "unit_of_measurement": info["unit"],
            "device": {"ids": ["gps_ntp_server"], "name": "GPS NTP Server"}
        }
        topic = f"homeassistant/sensor/{MQTT_TOPIC_PREFIX}_{entity_id}/config"
        mqtt_client.publish(topic, json.dumps(config_payload), retain=True)
    print("MQTT Discovery payloads sent.")

def telemetry_loop():
    """
    Background thread that polls GPS and Chrony stats and pushes them to MQTT.
    """
    global latest_snapshot
    while True:
        try:
            # 1. Gather data via Manager
            gps_data = gps_mgr.get_gps_data()
            chrony_stats = gps_mgr.get_chrony_stats()
            diag = gps_mgr.get_antenna_diagnostics(gps_data)
            constellations = gps_mgr.get_constellation_breakdown(gps_data)

            if gps_data:
                # Update global snapshot for Web UI
                latest_snapshot = {
                    "gps": gps_data,
                    "chrony": chrony_stats,
                    "diagnostics": diag,
                    "constellations": constellations,
                    "timestamp": time.time()
                }

                # 2. Publish to MQTT for Home Assistant
                mqtt_client.publish(f"{MQTT_TOPIC_PREFIX}_status", "Online")
                mqtt_client.publish(f"{MQTT_TOPIC_PREFIX}_sats", gps_data.get('sats_visible', 0))
                mqtt_client.publish(f"{MQTT_TOPIC_PREFIX}_antenna", diag['status'])
                mqtt_client.publish(f"{MQTT_TOPIC_PREFIX}_stratum", chrony_stats.get('stratum', 'N/A'))

        except Exception as e:
            print(f"Telemetry Error: {e}")
            mqtt_client.publish(f"{MQTT_TOPIC_PREFIX}_status", "Error")

        time.sleep(10) # Update every 10 seconds

# --- WEB UI ROUTES ---

@app.route('/')
def index():
    """Serves the main dashboard page."""
    return render_template('index.html')

@app.route('/api/stats')
def api_stats():
    if not latest_snapshot:
        return jsonify({"error": "No GPS data available yet"}), 503
    
    # Inject the most recent client list directly into the response
    latest_snapshot['clients'] = gps_mgr.get_ntp_clients() 
    return jsonify(latest_snapshot)


@app.route('/health')
def health():
    """HA Health Check endpoint."""
    status = "healthy" if latest_snapshot else "warning"
    return jsonify({"status": status, "uptime": time.time()}), 200

# --- MAIN EXECUTION ---

if __name__ == "__main__":
    # 1. Setup MQTT Connection
    try:
        mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
        mqtt_client.on_connect = on_connect
        mqtt_client.connect(MQTT_HOST, 1883, 60)
        mqtt_client.loop_start() # Start MQTT network loop in background
    except Exception as e:
        print(f"Could not connect to MQTT: {e}")

    # 2. Start Telemetry Thread
    t = threading.Thread(target=telemetry_loop, daemon=True)
    t.start()

    # 3. Run Web UI Server
    # Note: In a real HA addon, we use host 0.0.0.0 to be accessible on the network
    print("Starting Web Dashboard on port 8080...")
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)

from flask import Blueprint, jsonify, render_template
import time

# We create a Blueprint instead of a full App. 
# This allows main.py to "mount" these routes into the primary application.
web_bp = Blueprint('web_ui', __name__, template_folder='templates')

def create_web_server(gps_mgr):
    """
    This function wraps our routes so they have access to the 
    shared GPSManager instance created in main.py.
    """

    @web_bp.route('/')
    def index():
        """Serves the main NOC dashboard."""
        return render_template('index.html')

    @web_bp.route('/api/stats')
    def api_stats():
        """
        Provides a consolidated JSON payload of all system stats.
        This is what the Javascript in index.html calls every 3 seconds.
        """
        try:
            # Get raw data from hardware manager
            gps_data = gps_mgr.get_gps_data()
            chrony_stats = gps_mgr.get_chrony_stats()
            diag = gps_mgr.get_antenna_diagnostics(gps_data)
            constellations = gps_mgr.get_constellation_breakdown(gps_data)
            clients = gps_mgr.get_ntp_clients()

            if not gps_data:
                return jsonify({"error": "GPS device not providing data"}), 503

            # Construct the final payload for the frontend
            payload = {
                "gps": gps_data,
                "chrony": chrony_stats,
                "diagnostics": diag,
                "constellations": constellations,
                "clients": clients,
                "timestamp": time.time()
            }
            return jsonify(payload)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @web_bp.route('/health')
    def health():
        """Endpoint for Home Assistant Addon Health checks."""
        try:
            # If we can get GPS data, the system is healthy
            if gps_mgr.get_gps_data():
                return jsonify({"status": "healthy", "uptime": time.time()}), 200
            else:
                return jsonify({"status": "degraded", "reason": "No GPS fix"}), 200
        except Exception as e:
            return jsonify({"status": "unhealthy", "error": str(e)}), 500

    return web_bp

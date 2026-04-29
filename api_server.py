#!/usr/bin/env python3
"""
API Server - Flask Endpoints for Proteus Simulation
Handles REST API communication with main system
"""

import logging
import json
import threading
from flask import Flask, request, jsonify
from system_config import system_state, get_system_state
import gpio_simulation

logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# ============================================================================
# FLASK API ENDPOINTS
# ============================================================================

@app.route('/status', methods=['GET'])
def get_status():
    """Get current machine status"""
    state = get_system_state()
    logger.info(f"Status request - Current: {state['status']}")
    response = {
        "machine_name": state['team_name'],
        "status": state['status'],
        "power_on": state['power_on'],
        "downtime_triggered": state['downtime_triggered'],
        "timestamp": __import__('time').time()
    }
    print(f"[API] GET /status - Response: {json.dumps(response)}")
    return jsonify(response), 200

@app.route('/power_cut', methods=['POST'])
def handle_power_cut():
    """Handle power cut command"""
    data = request.get_json() or {}
    machine_name = data.get('machine_name')
    
    logger.info(f"Power cut request for machine: {machine_name}")
    print(f"[API] POST /power_cut - Machine: {machine_name}")
    
    if machine_name != system_state.team_name:
        logger.warning(f"Power cut for wrong machine: {machine_name}, expected {system_state.team_name}")
        return jsonify({"error": "Machine name mismatch"}), 400
    
    if system_state.power_on:
        system_state.power_on = False
        system_state.current_status = "offline"
        gpio_simulation.set_relay(22, True)
        logger.info("Power cut executed")
        print(f"[POWER] Machine powered OFF")
        return jsonify({
            "status": "success",
            "message": "Power cut executed",
            "machine": machine_name
        }), 200
    else:
        logger.info("Power cut request but already off")
        return jsonify({
            "status": "success",
            "message": "Power already off",
            "machine": machine_name
        }), 200

@app.route('/power_restore', methods=['POST'])
def handle_power_restore():
    """Handle power restore command"""
    data = request.get_json() or {}
    machine_name = data.get('machine_name')
    
    logger.info(f"Power restore request for machine: {machine_name}")
    print(f"[API] POST /power_restore - Machine: {machine_name}")
    
    if machine_name != system_state.team_name:
        logger.warning(f"Power restore for wrong machine: {machine_name}, expected {system_state.team_name}")
        return jsonify({"error": "Machine name mismatch"}), 400
    
    if not system_state.power_on:
        system_state.power_on = True
        system_state.current_status = "working"
        gpio_simulation.set_relay(22, False)
        logger.info("Power restored")
        print(f"[POWER] Machine powered ON")
        return jsonify({
            "status": "success",
            "message": "Power restored",
            "machine": machine_name
        }), 200
    else:
        logger.info("Power restore request but already on")
        return jsonify({
            "status": "success",
            "message": "Power already on",
            "machine": machine_name
        }), 200

@app.route('/event', methods=['POST'])
def handle_event():
    """Receive event notification from main system"""
    data = request.get_json() or {}
    event_type = data.get('event_type')
    machine_name = data.get('machine_name')
    
    logger.info(f"Event received: {event_type} for {machine_name}")
    print(f"[API] POST /event - Type: {event_type}, Machine: {machine_name}")
    
    return jsonify({
        "status": "success",
        "message": "Event received",
        "timestamp": __import__('time').time()
    }), 200

@app.route('/reset', methods=['POST'])
def handle_reset():
    """Reset system to idle state"""
    from button_monitor import reset_system
    
    data = request.get_json() or {}
    machine_name = data.get('machine_name')
    
    logger.info(f"Reset request for machine: {machine_name}")
    print(f"[API] POST /reset - Machine: {machine_name}")
    
    if machine_name != system_state.team_name:
        return jsonify({"error": "Machine name mismatch"}), 400
    
    reset_system()
    
    return jsonify({
        "status": "success",
        "message": "System reset",
        "machine": machine_name
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "machine": system_state.team_name,
        "timestamp": __import__('time').time()
    }), 200

@app.route('/api/docs', methods=['GET'])
def api_docs():
    """API documentation"""
    docs = {
        "endpoints": {
            "GET /health": "Health check",
            "GET /status": "Get current status",
            "POST /power_cut": "Cut machine power",
            "POST /power_restore": "Restore machine power",
            "POST /event": "Receive event notification",
            "POST /reset": "Reset system to idle",
        },
        "example_payloads": {
            "power_cut": {"machine_name": "PROTEUS_SIM"},
            "power_restore": {"machine_name": "PROTEUS_SIM"},
        }
    }
    return jsonify(docs), 200

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    logger.error(f"Server error: {error}")
    return jsonify({"error": "Internal server error"}), 500

# ============================================================================
# FLASK SERVER STARTUP
# ============================================================================

def start_flask_server():
    """Start Flask API server in background thread"""
    def run_flask():
        logger.info("Starting Flask API server on http://0.0.0.0:5001")
        print("[API] Flask server starting on http://0.0.0.0:5001")
        try:
            app.run(
                host='0.0.0.0',
                port=5001,
                debug=False,
                use_reloader=False,
                threaded=True
            )
        except Exception as e:
            logger.error(f"Flask server error: {e}")
            print(f"[API ERROR] {e}")
    
    thread = threading.Thread(target=run_flask, daemon=True)
    thread.start()
    return thread

if __name__ == '__main__':
    # For testing the Flask app directly
    app.run(host='0.0.0.0', port=5001, debug=True)

#!/usr/bin/env python3
"""
System Configuration - Proteus Simulation
"""

import logging
import time

# Setup logging
logging.basicConfig(
    filename='proteus_simulation.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# GPIO PIN CONFIGURATION
# ============================================================================

# LED Pins (Outputs)
LED_PINS = {
    'DOWNTIME': 26,
    'MAINTENANCE': 20,
    'BREAK': 16,
    'DOWNTIME_ALERT': 7,
    'CANCEL': 13,
    'SYSTEM_RESET': 17,
}

# Button Pins (Inputs)
BUTTON_PINS = {
    'CHANGING_MATERIAL': 19,
    'MAINTENANCE': 21,
    'BREAK': 12,
    'CANCEL': 6,
    'SYSTEM_RESET': 27,
    'POWER_CUT': 8,
}

# Sensor Pins (Inputs)
SENSOR_PINS = {
    'OBSTACLE': 1,
}

# Relay Pins (Outputs)
RELAY_PINS = {
    'POWER': 22,
}

# ============================================================================
# SYSTEM STATE
# ============================================================================

class SystemState:
    """Global system state manager"""
    
    def __init__(self):
        self.team_name = "PROTEUS_SIM"
        self.current_status = "working"
        self.power_on = True
        self.downtime_triggered = False
        self.selected_led = None
        self.event_start_time = None
        self.material_change_active = False
        self.material_change_start_time = None
        self.maintenance_state = None
        self.maintenance_arrival_time = None
        self.last_sensor_trigger = time.time()
        
        # LED state tracking
        self.led_states = {pin: False for pin in LED_PINS.values()}
        
        # Button state tracking
        self.button_states = {pin: True for pin in BUTTON_PINS.values()}
        
        # Sensor state tracking
        self.sensor_states = {pin: True for pin in SENSOR_PINS.values()}

# Global singleton
system_state = SystemState()

def initialize_system():
    """Initialize the system"""
    logger.info(f"System initialized - Machine: {system_state.team_name}")
    print(f"[INIT] Machine: {system_state.team_name}")
    print(f"[INIT] Status: {system_state.current_status}")
    print(f"[INIT] Power: {'ON' if system_state.power_on else 'OFF'}")

def log_event(event_name, details=""):
    """Log an event"""
    msg = f"[{event_name}] {details}"
    logger.info(msg)
    print(msg)

def get_system_state():
    """Get current system state"""
    return {
        'team_name': system_state.team_name,
        'status': system_state.current_status,
        'power_on': system_state.power_on,
        'downtime_triggered': system_state.downtime_triggered,
        'selected_led': system_state.selected_led,
        'material_change_active': system_state.material_change_active,
    }

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Proteus Simulation - Machine Maintenance System
Adapted from Raspberry Pi GPIO code for Proteus circuit simulation
"""

import time
import threading
import logging
import json
import socket
import traceback
import sys
from threading import Thread

# Force unbuffered output for Proteus (with fallback for StdoutCatcher)
try:
    sys.stdout = open(sys.stdout.fileno(), mode='w', buffering=1, encoding='utf8')
    sys.stderr = open(sys.stderr.fileno(), mode='w', buffering=1, encoding='utf8')
except (AttributeError, OSError):
    # Proteus VSM uses StdoutCatcher which doesn't support fileno()
    # Just use default stdout/stderr with explicit flush() calls
    pass

# For Proteus simulation - GPIO Interface
PROTEUS_MODE = True
try:
    import pio  # Proteus I/O module
    import resource
except ImportError:
    PROTEUS_MODE = False
    print("NOTE: Proteus I/O not available - using simulation mode")

# Setup logging - output to both file and console
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('button_log.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# GPIO PIN MAPPING FOR PROTEUS - 4 Button System with LM016L LCD
# ============================================================================

# LED Pin Mappings (Outputs) - 4 LEDs
LED_DOWNTIME = 26
LED_MATERIAL_CHANGE = 20
LED_BREAK = 16
LED_CANCEL = 12

# Button Pin Mappings (Inputs) - 4 Buttons
BUTTON_DOWNTIME = 6
BUTTON_MATERIAL_CHANGE = 19
BUTTON_BREAK = 21
BUTTON_CANCEL = 27

# Sensor Pin
SENSOR_OBSTACLE = 1

# I2C LCD Configuration (LM016L)
LCD_ADDRESS = 0x27  # Standard I2C address for 16x2 LCD module
LCD_BUS = 1  # I2C bus number (bus 1 on Raspberry Pi)
LCD = None  # LCD object (initialized later)

# ============================================================================
# GLOBAL STATE VARIABLES
# ============================================================================
TEAM_NAME = None
last_sensor_trigger = time.time()
downtime_triggered = False
selected_led = None
is_first_run = True
event_start_time = None
awaiting_user_id = False
start_user_id = None
start_comment = None
end_comment = None
sensor_alert_active = False
current_status = "working"
material_change_start_time = None
material_change_active = False

# Pin state tracking (for rising/falling edge detection)
pin_states = {
    SENSOR_OBSTACLE: True,
    BUTTON_DOWNTIME: True,
    BUTTON_MATERIAL_CHANGE: True,
    BUTTON_BREAK: True,
    BUTTON_CANCEL: True,
}

# ============================================================================
# PROTEUS PIN I/O FUNCTIONS
# ============================================================================

def setup_gpio():
    """Initialize GPIO pins for Proteus simulation"""
    try:
        if PROTEUS_MODE:
            logger.info("GPIO setup for Proteus simulation")
            # In Proteus, pins are configured through the circuit designer
            # This is a placeholder for actual Proteus configuration
            print("Proteus GPIO initialization (via circuit diagram)")
        else:
            logger.info("GPIO setup for stub simulation")
        
        turn_on_all_leds_test()
        logger.info("GPIO setup completed")
    except Exception as e:
        logger.error(f"GPIO setup error: {e}")
        print(f"GPIO setup error: {e}")

def turn_on_all_leds_test():
    """Test all LEDs on startup"""
    leds = [LED_DOWNTIME, LED_MATERIAL_CHANGE, LED_BREAK, LED_CANCEL]
    logger.info("Starting LED test - turning on all LEDs for 2 seconds")
    print("LED Test: Turning on all LEDs for 2 seconds...")
    
    for led in leds:
        set_led(led, True)
    
    time.sleep(2)
    
    for led in leds:
        set_led(led, False)
    
    logger.info("LED test completed")

def set_led(pin, state):
    """Set LED state (True=ON, False=OFF) - Proteus GPIO Output"""
    try:
        if PROTEUS_MODE:
            # Proteus: Write HIGH (1) or LOW (0) to GPIO pin
            # The pin must be configured as OUTPUT in your Proteus circuit
            gpio_value = 1 if state else 0
            # pio.digitalwrite(pin, gpio_value)  # Uncomment when in Proteus
            pass
        status = 'ON' if state else 'OFF'
        logger.debug(f"LED (pin {pin}): {status}")
        print("[LED] GPIO {0}: {1}".format(pin, status))
        sys.stdout.flush()
    except Exception as e:
        logger.error(f"Error setting LED {pin}: {e}")

def set_relay(pin, state):
    """Set relay state (True=ON, False=OFF) - Proteus GPIO Output"""
    try:
        if PROTEUS_MODE:
            # Proteus: Write HIGH (1) or LOW (0) to GPIO pin
            # The pin must be configured as OUTPUT in your Proteus circuit
            gpio_value = 1 if state else 0
            # pio.digitalwrite(pin, gpio_value)  # Uncomment when in Proteus
            pass
        logger.debug(f"Relay (pin {pin}): {'ON' if state else 'OFF'}")
        print(f"[GPIO {pin}] Relay: {'ON' if state else 'OFF'}")
    except Exception as e:
        logger.error(f"Error setting relay {pin}: {e}")

def read_button(pin):
    """Read button state - Proteus GPIO Input"""
    try:
        if PROTEUS_MODE:
            # Proteus: Read digital input from GPIO pin
            # Button HIGH (1) = released, LOW (0) = pressed
            # button_state = pio.digitalread(pin)  # Uncomment when in Proteus
            button_state = True  # Default to released
            return button_state
        return True
    except Exception as e:
        logger.error(f"Error reading button {pin}: {e}")
        return True

def read_sensor(pin):
    """Read sensor state - Proteus GPIO Input"""
    try:
        if PROTEUS_MODE:
            # Proteus: Read digital input from sensor GPIO pin
            # Sensor HIGH (1) = no obstacle, LOW (0) = obstacle detected
            # sensor_state = pio.digitalread(pin)  # Uncomment when in Proteus
            sensor_state = True  # Default to no obstacle
            return sensor_state
        return True
    except Exception as e:
        logger.error(f"Error reading sensor {pin}: {e}")
        return True

# ============================================================================
# I2C LCD DISPLAY FUNCTIONS
# ============================================================================

class LCD_I2C:
    """Virtual LCD display for Proteus simulation (console-based)"""
    
    def __init__(self, address=0x27, bus=1):
        self.address = address
        self.bus_num = bus
        self.connected = True  # Always connected in simulation
        self.line1 = ""
        self.line2 = ""
        logger.info(f"LM016L LCD initialized on I2C address 0x{self.address:02x}")
        print("[LCD] LM016L Display Ready at I2C 0x{0:02x}".format(self.address))
        self.display_text("", "")
    
    def display_text(self, line1, line2=""):
        """Display text on LCD (line1 and line2)"""
        # Truncate to 16 characters per line
        line1 = str(line1)[:16].ljust(16)
        line2 = str(line2)[:16].ljust(16)
        
        # Only update if content changed
        if line1 == self.line1 and line2 == self.line2:
            return
        
        self.line1 = line1
        self.line2 = line2
        
        # LM016L LCD display format (ASCII safe for Proteus)
        print("\n+---- LM016L LCD -+")
        print("|" + line1 + "|")
        print("|" + line2 + "|")
        print("+----------------+\n")
        sys.stdout.flush()
        
        logger.debug(f"LCD: '{line1}' / '{line2}'")

def init_lcd_display():
    """Initialize LCD display"""
    global LCD
    LCD = LCD_I2C(0x27, 1)
    if LCD.connected:
        LCD.display_text("System Starting", "Initializing...")

def update_lcd(line1, line2=""):
    """Update LCD display (or console if not connected)"""
    global LCD
    if LCD is None:
        return
    LCD.display_text(line1, line2)

# ============================================================================
# EVENT AND STATE MANAGEMENT
# ============================================================================

def send_event_async(event_type, duration=None, start_user_id=None, end_user_id=None, 
                     start_comment=None, end_comment=None, cancel_reason=None, 
                     reaction_time=None, maintenance_arrival_user_id=None, breakdown=None):
    """Send event to main API asynchronously"""
    if TEAM_NAME is None:
        logger.error("Cannot send event: TEAM_NAME not set")
        return
    
    def send_request():
        try:
            # API endpoint (commented out for basic Proteus simulation)
            # url = f"{MAIN_API_BASE_URL}/events/{event_type}/{TEAM_NAME}"
            data = {
                "machine": TEAM_NAME,
                "duration": duration,
                "start_user_id": start_user_id or "N/A",
                "end_user_id": end_user_id or "N/A",
                "start_comment": start_comment or "",
                "end_comment": end_comment or "",
                "cancel_reason": cancel_reason or "",
                "reaction_time": reaction_time,
                "maintenance_arrival_user_id": maintenance_arrival_user_id or "N/A",
                "breakdown": breakdown
            }
            # Log event data
            logger.info(f"Event: {event_type} - Details: {json.dumps(data)}")
            print(f"[EVENT_LOG] {event_type} for {TEAM_NAME}")
            
            # In Proteus simulation, API connection is disabled
            # Uncomment below if connecting to real API:
            # response = requests.post(url, json=data, timeout=5)
        except Exception as e:
            logger.error(f"Error processing {event_type} event: {e}")
            print(f"[ERROR] {event_type}: {e}")
    
    Thread(target=send_request, daemon=True).start()

def reset_system(event_type=None, end_user_id=None, end_comment=None, 
                 cancel_reason=None, breakdown=None):
    """Reset system to idle state"""
    global last_sensor_trigger, downtime_triggered, selected_led, is_first_run
    global event_start_time, awaiting_user_id, start_user_id, start_comment
    global sensor_alert_active, current_status
    global material_change_start_time, material_change_active
    
    duration = None
    
    if event_type and event_start_time:
        duration = time.time() - event_start_time
        log_msg = f"Event {event_type} ended for {TEAM_NAME}. Duration: {duration:.2f}s"
        logger.info(log_msg)
        print(log_msg)
        
        event_prefix = "cancel_" if cancel_reason else "reset_"
        send_event_async(
            f"{event_prefix}{event_type}",
            duration, start_user_id, end_user_id,
            start_comment, end_comment, cancel_reason
        )
    
    # Reset all LEDs to idle state (4-Button System)
    set_led(LED_DOWNTIME, False)
    set_led(LED_MATERIAL_CHANGE, False)
    set_led(LED_BREAK, False)
    set_led(LED_CANCEL, False)
    
    # Reset global state
    last_sensor_trigger = time.time()
    downtime_triggered = False
    selected_led = None
    event_start_time = None
    start_user_id = None
    start_comment = None
    end_comment = None
    is_first_run = True
    awaiting_user_id = False
    sensor_alert_active = False
    material_change_start_time = None
    material_change_active = False
    current_status = "working"
    
    logger.info("System reset to idle state")
    print("[SYSTEM] Reset to idle state")
    sys.stdout.flush()

def selected_led_to_event_type(led):
    """Convert selected LED to event type (4-Button System)"""
    if led == LED_DOWNTIME:
        return "downtime"
    elif led == LED_BREAK:
        return "break"
    else:
        return "other"

# ============================================================================
# FLASK API ENDPOINTS (Disabled for basic Proteus simulation - no Flask dependency)
# ============================================================================
# API endpoints removed to avoid Flask import requirement
# Can be re-enabled later if needed

# ============================================================================
# BUTTON AND SENSOR MONITORING
# ============================================================================

def monitor_buttons_and_sensors():
    """Main monitoring loop - 4 button system with LM016L LCD"""
    global downtime_triggered, selected_led, is_first_run, event_start_time
    global start_user_id, start_comment, current_status
    global material_change_active, material_change_start_time, last_sensor_trigger
    
    logger.info("Button and sensor monitoring started (4-Button System)")
    print("[MONITOR] Ready: Downtime | Material | Break | Cancel\n")
    
    prev_states = pin_states.copy()
    
    try:
        while True:
            # Read current pin states
            curr_sensor = read_sensor(SENSOR_OBSTACLE)
            curr_btn_downtime = read_button(BUTTON_DOWNTIME)
            curr_btn_material = read_button(BUTTON_MATERIAL_CHANGE)
            curr_btn_break = read_button(BUTTON_BREAK)
            curr_btn_cancel = read_button(BUTTON_CANCEL)
            
            # Check for downtime after 20 seconds without sensor trigger
            if (time.time() - last_sensor_trigger > 20 and not downtime_triggered 
                and not selected_led and not material_change_active):
                logger.info(f"Downtime alert triggered for {TEAM_NAME}")
                print("[ALERT] Downtime detected!")
                sys.stdout.flush()
                update_lcd("DOWNTIME ALERT", "Press button...")
                downtime_triggered = True
                is_first_run = False
                current_status = "downtime"
                set_led(LED_DOWNTIME, True)
                set_led(LED_MATERIAL_CHANGE, False)
                set_led(LED_BREAK, False)
            
            # Material change timeout (180 seconds)
            if (material_change_active and 
                time.time() - material_change_start_time > 180):
                logger.info("Material change timeout")
                print("[MATERIAL] Timeout - Back to idle")
                sys.stdout.flush()
                update_lcd("Material Timeout", "Back to idle")
                material_change_active = False
                downtime_triggered = True
                current_status = "downtime"
                set_led(LED_MATERIAL_CHANGE, False)
                set_led(LED_DOWNTIME, True)
            
            # Button: DOWNTIME
            if prev_states[BUTTON_DOWNTIME] and not curr_btn_downtime:
                logger.info("Downtime button pressed")
                print("[BUTTON] Downtime pressed")
                sys.stdout.flush()
                if not selected_led:
                    selected_led = LED_DOWNTIME
                    downtime_triggered = False
                    event_start_time = time.time()
                    start_user_id = f"USER_{int(time.time())}"
                    current_status = "downtime"
                    set_led(LED_DOWNTIME, True)
                    update_lcd("DOWNTIME", "Event started")
                    print("[EVENT] Downtime event started")
                    sys.stdout.flush()
                    send_event_async("downtime", start_user_id=start_user_id)
            
            # Button: MATERIAL CHANGE
            if prev_states[BUTTON_MATERIAL_CHANGE] and not curr_btn_material:
                logger.info("Material change button pressed")
                print("[BUTTON] Material Change pressed")
                sys.stdout.flush()
                if material_change_active:
                    material_change_active = False
                    set_led(LED_MATERIAL_CHANGE, False)
                    print("[MATERIAL] Change stopped")
                    sys.stdout.flush()
                    update_lcd("Material Complete", "Back to idle")
                elif not selected_led:
                    material_change_active = True
                    material_change_start_time = time.time()
                    set_led(LED_MATERIAL_CHANGE, True)
                    print("[MATERIAL] Change started (180s)")
                    sys.stdout.flush()
                    update_lcd("Material Change", "180 sec timer")
                    send_event_async("material_change",  start_user_id=f"USER_{int(time.time())}")
            
            # Button: BREAK
            if prev_states[BUTTON_BREAK] and not curr_btn_break:
                logger.info("Break button pressed")
                print("[BUTTON] Break pressed")
                sys.stdout.flush()
                if selected_led == LED_BREAK:
                    duration = time.time() - event_start_time
                    print("[BREAK] Ended - Duration: {0:.2f}s".format(duration))
                    sys.stdout.flush()
                    update_lcd("Break Ended", "Duration: {0:.0f}s".format(duration))
                    reset_system("break")
                elif not selected_led:
                    selected_led = LED_BREAK
                    downtime_triggered = False
                    event_start_time = time.time()
                    start_user_id = f"USER_{int(time.time())}"
                    current_status = "break"
                    set_led(LED_BREAK, True)
                    set_led(LED_DOWNTIME, False)
                    print("[EVENT] Break started")
                    sys.stdout.flush()
                    update_lcd("BREAK TIME", "Started...")
                    send_event_async("break", start_user_id=start_user_id)
            
            # Button: CANCEL
            if prev_states[BUTTON_CANCEL] and not curr_btn_cancel:
                logger.info("Cancel button pressed")
                print("[BUTTON] Cancel pressed")
                sys.stdout.flush()
                if selected_led:
                    if selected_led == LED_DOWNTIME:
                        event_type = "downtime"
                    elif selected_led == LED_BREAK:
                        event_type = "break"
                    else:
                        event_type = "other"
                    print("[CANCEL] {0} cancelled".format(event_type))
                    sys.stdout.flush()
                    update_lcd("EVENT CANCELLED", event_type.upper())
                    reset_system(event_type, cancel_reason="User cancelled")
            
            # Update previous states
            prev_states = {
                SENSOR_OBSTACLE: curr_sensor,
                BUTTON_DOWNTIME: curr_btn_downtime,
                BUTTON_MATERIAL_CHANGE: curr_btn_material,
                BUTTON_BREAK: curr_btn_break,
                BUTTON_CANCEL: curr_btn_cancel,
            }
            
            time.sleep(0.01)  # 10ms polling interval
    
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user")
        print("\n[MONITOR] Stopped")
        sys.stdout.flush()
    except Exception as e:
        logger.error(f"Monitor loop error: {e}\n{traceback.format_exc()}")
        print("[ERROR] Monitor loop crashed: {0}".format(str(e)))
        sys.stdout.flush()

# ============================================================================
# INITIALIZATION AND MAIN
# ============================================================================

def get_machine_name():
    """Get machine name (simulated for Proteus)"""
    global TEAM_NAME
    TEAM_NAME = "PROTEUS_SIMULATION"
    logger.info(f"Machine name set to: {TEAM_NAME}")
    print("[INIT] Machine: {0}".format(TEAM_NAME))
    sys.stdout.flush()

def main():
    """Main entry point"""
    try:
        # Immediate startup message
        print("\n")
        print("="*70)
        print("PROTEUS SIMULATION - Machine Maintenance System")
        print("="*70)
        print("[STARTUP] System initialization starting...")
        sys.stdout.flush()
        
        logger.info("========== SYSTEM START ==========")
        
        get_machine_name()
        print("[INIT] Setting up GPIO...")
        sys.stdout.flush()
        
        setup_gpio()
        print("[INIT] Initializing LCD display...")
        sys.stdout.flush()
        
        init_lcd_display()
        
        print(f"\n[{TEAM_NAME}] Ready for operation!\n")
        print("="*70)
        print("Available controls (4-Button System):")
        print("-"*70)
        print("  GPIO 6  -> Button Downtime: Start downtime event")
        print("  GPIO 19 -> Button Material Change: Start/stop material (180s)")
        print("  GPIO 21 -> Button Break: Start/end break event")
        print("  GPIO 27 -> Button Cancel: Cancel current event")
        print("  GPIO 1  -> Sensor: Detects machine activity")
        print("="*70 + "\n")
        sys.stdout.flush()
        
        update_lcd("System Ready", "4-Button Ready")
        print("[MONITOR] Starting button/sensor monitoring...")
        print("[MONITOR] Waiting for button presses...\n")
        sys.stdout.flush()
        
        # Start monitoring loop (no Flask API for basic simulation)
        monitor_buttons_and_sensors()
    
    except Exception as e:
        logger.error(f"Main error: {e}\n{traceback.format_exc()}")
        print(f"[ERROR] {e}")
        print(traceback.format_exc())
        sys.stdout.flush()
    finally:
        logger.info("========== SYSTEM SHUTDOWN ==========")
        print("\n[SHUTDOWN] System stopped")
        sys.stdout.flush()

if __name__ == "__main__":
    main()

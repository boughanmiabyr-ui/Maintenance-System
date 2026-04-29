#!/usr/bin/env python3
"""
Button Monitor - Proteus Hardware Interface
Simulates button presses and sensor inputs
"""

import logging
import time
import threading
from system_config import system_state, BUTTON_PINS, SENSOR_PINS
import gpio_simulation

logger = logging.getLogger(__name__)

# Button press history for detecting edges
button_history = {}
last_sensor_time = time.time()

# ============================================================================
# SIMULATED BUTTON INPUT
# ============================================================================

def read_button(pin):
    """Read button state from GPIO (simulated)"""
    # In real Proteus: read actual GPIO input
    # For simulation: return True (released) by default
    return button_history.get(pin, True)  # True = released, False = pressed

def read_sensor(pin):
    """Read sensor state from GPIO (simulated)"""
    # In real Proteus: read actual sensor input
    # For simulation: return True (no obstruction) by default
    return system_state.sensor_states.get(pin, True)

def simulate_button_press(button_name):
    """Simulate a button press (for testing)"""
    pin = BUTTON_PINS.get(button_name)
    if pin:
        logger.info(f"Simulated button press: {button_name} (GPIO {pin})")
        print(f"\n>>> BUTTON PRESS SIMULATED: {button_name} <<<\n")
        button_history[pin] = False  # Pressed
        time.sleep(0.1)
        button_history[pin] = True   # Released

def simulate_sensor_trigger():
    """Simulate sensor obstacle detection"""
    pin = SENSOR_PINS['OBSTACLE']
    logger.info(f"Simulated sensor trigger: OBSTACLE (GPIO {pin})")
    print(f"\n>>> SENSOR TRIGGERED: OBSTACLE DETECTED <<<\n")
    system_state.sensor_states[pin] = False  # Obstacle detected
    time.sleep(0.1)
    system_state.sensor_states[pin] = True   # Obstacle gone

# ============================================================================
# BUTTON EVENT HANDLERS
# ============================================================================

def handle_power_cut_press():
    """Handle power cut button press"""
    print(f"\n[POWER CONTROL] Power Cut button pressed")
    if system_state.power_on:
        system_state.power_on = False
        system_state.current_status = "offline"
        gpio_simulation.set_relay(22, True)
        logger.info("Power cut: Machine turned OFF")
    else:
        system_state.power_on = True
        system_state.current_status = "working"
        gpio_simulation.set_relay(22, False)
        logger.info("Power restored: Machine turned ON")

def handle_material_change_press():
    """Handle material change button press"""
    print(f"\n[MATERIAL CHANGE] Button pressed")
    if system_state.material_change_active:
        system_state.material_change_active = False
        logger.info("Material change stopped")
    else:
        system_state.material_change_active = True
        system_state.material_change_start_time = time.time()
        logger.info("Material change started (180 second countdown)")

def handle_maintenance_press():
    """Handle maintenance button press"""
    print(f"\n[MAINTENANCE] Button pressed")
    if system_state.selected_led == 20:  # LED_MAINTENANCE
        if system_state.maintenance_state == "started":
            system_state.maintenance_state = "arrived"
            system_state.maintenance_arrival_time = time.time()
            reaction_time = system_state.maintenance_arrival_time - system_state.event_start_time
            logger.info(f"Maintenance arrived. Reaction time: {reaction_time:.2f}s")
            print(f"[MAINTENANCE] Arrived - Reaction time: {reaction_time:.2f} seconds")
        elif system_state.maintenance_state == "arrived":
            duration = time.time() - system_state.event_start_time
            logger.info(f"Maintenance ended. Duration: {duration:.2f}s")
            print(f"[MAINTENANCE] Ended - Duration: {duration:.2f} seconds")
            reset_event("maintenance")
    elif system_state.downtime_triggered and not system_state.selected_led:
        system_state.selected_led = 20  # LED_MAINTENANCE
        system_state.downtime_triggered = False
        system_state.event_start_time = time.time()
        system_state.maintenance_state = "started"
        system_state.current_status = "maintenance"
        print(f"[MAINTENANCE] Event started")
        logger.info("Maintenance event started")
        gpio_simulation.set_led(20, True)
        gpio_simulation.set_led(7, True)  # Downtime alert off

def handle_break_press():
    """Handle break button press"""
    print(f"\n[BREAK] Button pressed")
    if system_state.selected_led == 16:  # LED_BREAK
        duration = time.time() - system_state.event_start_time
        logger.info(f"Break ended. Duration: {duration:.2f}s")
        print(f"[BREAK] Ended - Duration: {duration:.2f} seconds")
        reset_event("break")
    elif system_state.downtime_triggered and not system_state.selected_led:
        system_state.selected_led = 16  # LED_BREAK
        system_state.downtime_triggered = False
        system_state.event_start_time = time.time()
        system_state.current_status = "break"
        print(f"[BREAK] Event started")
        logger.info("Break event started")
        gpio_simulation.set_led(16, True)
        gpio_simulation.set_led(7, True)  # Downtime alert off

def handle_cancel_press():
    """Handle cancel button press"""
    print(f"\n[CANCEL] Button pressed")
    if system_state.selected_led:
        event_name = {26: "downtime", 20: "maintenance", 16: "break"}.get(
            system_state.selected_led, "unknown"
        )
        logger.info(f"Event cancelled: {event_name}")
        print(f"[CANCEL] Event cancelled: {event_name}")
        reset_event(event_name, cancelled=True)

def handle_system_reset_press():
    """Handle system reset button press"""
    print(f"\n[SYSTEM] Reset button pressed")
    logger.info("System reset triggered")
    reset_system()

def reset_event(event_type, cancelled=False):
    """Reset system after event completion"""
    duration = time.time() - system_state.event_start_time if system_state.event_start_time else 0
    logger.info(f"{event_type.title()} event ended. Duration: {duration:.2f}s")
    reset_system()

def reset_system():
    """Reset system to idle state"""
    system_state.selected_led = None
    system_state.downtime_triggered = False
    system_state.event_start_time = None
    system_state.material_change_active = False
    system_state.material_change_start_time = None
    system_state.maintenance_state = None
    system_state.current_status = "working"
    
    gpio_simulation.reset_all_leds()
    logger.info("System reset to idle")
    print(f"\n[SYSTEM] Reset to idle state\n")

# ============================================================================
# BUTTON MONITORING LOOP
# ============================================================================

def check_buttons():
    """Check buttons (called in main loop)"""
    # This function is called frequently from the main loop
    # In real Proteus, this would read actual GPIO inputs
    pass

def start_monitoring():
    """Start button monitoring in background thread"""
    def monitoring_thread():
        """Background monitor thread"""
        logger.info("Button monitoring started")
        print("\n[MONITOR] Button monitoring active")
        print("Ready to receive simulated button presses\n")
        
        prev_states = {pin: True for pin in BUTTON_PINS.values()}
        
        try:
            while True:
                # Read current button states
                curr_states = {pin: read_button(pin) for pin in BUTTON_PINS.values()}
                
                # Check for falling edge (high to low) - button press
                for pin, curr_state in curr_states.items():
                    if prev_states[pin] and not curr_state:
                        # Button pressed (falling edge)
                        button_name = next(
                            (name for name, p in BUTTON_PINS.items() if p == pin),
                            f"BUTTON_{pin}"
                        )
                        
                        if pin == BUTTON_PINS['POWER_CUT']:
                            handle_power_cut_press()
                        elif pin == BUTTON_PINS['CHANGING_MATERIAL']:
                            handle_material_change_press()
                        elif pin == BUTTON_PINS['MAINTENANCE']:
                            handle_maintenance_press()
                        elif pin == BUTTON_PINS['BREAK']:
                            handle_break_press()
                        elif pin == BUTTON_PINS['CANCEL']:
                            handle_cancel_press()
                        elif pin == BUTTON_PINS['SYSTEM_RESET']:
                            handle_system_reset_press()
                
                # Check for downtime trigger (20 seconds without activity)
                if (time.time() - system_state.last_sensor_trigger > 20 and 
                    not system_state.downtime_triggered and 
                    not system_state.selected_led and
                    not system_state.material_change_active):
                    system_state.downtime_triggered = True
                    system_state.current_status = "downtime"
                    logger.info("Downtime alert triggered")
                    print(f"\n[ALERT] DOWNTIME - No activity for 20 seconds")
                    gpio_simulation.turn_on_downtime_alert()
                
                # Material change timeout (180 seconds)
                if (system_state.material_change_active and 
                    system_state.material_change_start_time and
                    time.time() - system_state.material_change_start_time > 180):
                    system_state.material_change_active = False
                    system_state.downtime_triggered = True
                    system_state.current_status = "downtime"
                    logger.info("Material change timeout - downtime triggered")
                    print(f"\n[ALERT] DOWNTIME - Material change timeout")
                    gpio_simulation.turn_on_downtime_alert()
                
                prev_states = curr_states
                time.sleep(0.01)  # 10ms polling
        
        except KeyboardInterrupt:
            logger.info("Button monitoring stopped")
            print("\n[MONITOR] Stopped")
    
    thread = threading.Thread(target=monitoring_thread, daemon=True)
    thread.start()
    return thread

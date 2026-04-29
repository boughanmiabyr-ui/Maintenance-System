#!/usr/bin/env python3
"""
GPIO Simulation - Proteus Hardware Interface
Handles LED and relay control
"""

import logging
import time
from system_config import system_state, LED_PINS, RELAY_PINS, SENSOR_PINS, BUTTON_PINS

logger = logging.getLogger(__name__)

# Color codes for console output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

# ============================================================================
# LED CONTROL
# ============================================================================

def setup_gpio():
    """Initialize GPIO (Proteus simulation)"""
    logger.info("GPIO Setup - Proteus Simulation Mode")
    print(f"{YELLOW}[GPIO SETUP]{RESET}")
    for name, pin in LED_PINS.items():
        print(f"  - LED {name} on GPIO {pin}: OFF")
    for name, pin in RELAY_PINS.items():
        print(f"  - RELAY {name} on GPIO {pin}: OFF")
    for name, pin in BUTTON_PINS.items():
        print(f"  - BUTTON {name} on GPIO {pin}: READY")
    for name, pin in SENSOR_PINS.items():
        print(f"  - SENSOR {name} on GPIO {pin}: READY")
    
    # Test sequence - turn on all LEDs for 2 seconds
    print(f"\n{YELLOW}[LED TEST]{RESET} Turning on all LEDs for 2 seconds...")
    for led_name, led_pin in LED_PINS.items():
        set_led(led_pin, True)
    time.sleep(2)
    for led_name, led_pin in LED_PINS.items():
        set_led(led_pin, False)
    print("LED test complete\n")

def set_led(pin, state):
    """Set LED state"""
    if pin in system_state.led_states:
        system_state.led_states[pin] = state
        
        # Find LED name
        led_name = next((name for name, p in LED_PINS.items() if p == pin), f"LED_{pin}")
        
        if state:
            print(f"{GREEN}[LED ON ]{RESET} {led_name} (GPIO {pin})")
            logger.debug(f"LED {led_name} (GPIO {pin}) turned ON")
        else:
            print(f"{RED}[LED OFF]{RESET} {led_name} (GPIO {pin})")
            logger.debug(f"LED {led_name} (GPIO {pin}) turned OFF")

def set_relay(pin, state):
    """Set relay state"""
    relay_name = next((name for name, p in RELAY_PINS.items() if p == pin), f"RELAY_{pin}")
    
    if state:
        print(f"{GREEN}[RELAY ON ]{RESET} {relay_name} (GPIO {pin})")
        logger.debug(f"Relay {relay_name} (GPIO {pin}) turned ON")
    else:
        print(f"{RED}[RELAY OFF]{RESET} {relay_name} (GPIO {pin})")
        logger.debug(f"Relay {relay_name} (GPIO {pin}) turned OFF")

def update_leds():
    """Update LED states (called in main loop)"""
    # This can be expanded for blinking LEDs, animations, etc.
    pass

def turn_on_alert_leds():
    """Turn on all alert LEDs"""
    for led_pin in LED_PINS.values():
        if led_pin != LED_PINS['DOWNTIME_ALERT']:
            set_led(led_pin, True)

def turn_off_alert_leds():
    """Turn off all alert LEDs"""
    for led_pin in LED_PINS.values():
        set_led(led_pin, False)

def turn_on_downtime_alert():
    """Activate downtime alert state"""
    set_led(LED_PINS['DOWNTIME_ALERT'], False)
    set_led(LED_PINS['DOWNTIME'], True)
    set_led(LED_PINS['MAINTENANCE'], True)
    set_led(LED_PINS['BREAK'], True)
    set_led(LED_PINS['CANCEL'], True)
    set_led(LED_PINS['SYSTEM_RESET'], True)

def reset_all_leds():
    """Reset to idle state (all LEDs off except alert)"""
    set_led(LED_PINS['DOWNTIME'], False)
    set_led(LED_PINS['MAINTENANCE'], False)
    set_led(LED_PINS['BREAK'], False)
    set_led(LED_PINS['DOWNTIME_ALERT'], True)
    set_led(LED_PINS['CANCEL'], False)
    set_led(LED_PINS['SYSTEM_RESET'], False)
    set_relay(RELAY_PINS['POWER'], False)

def cleanup_gpio():
    """Clean up GPIO on shutdown"""
    logger.info("GPIO Cleanup")
    reset_all_leds()
    print(f"\n{YELLOW}[GPIO CLEANUP]{RESET} All LEDs reset to idle state")

#!/usr/bin/env python3
"""
Proteus RPI3 Circuit Simulation - Minimal Version
This is the actual Proteus main.py file to use in your simulation project
"""

# Proteus Modules
from goto import *
import time
import var
import pio
import resource

# Custom modules for this simulation
import system_config
import gpio_simulation
import button_monitor
import api_server

# ============================================================================
# PERIPHERAL CONFIGURATION (Proteus auto-generated)
# ============================================================================

import cpu
import FileStore
import VFP

def peripheral_setup():
    """Initialize Proteus peripherals"""
    # Peripheral Constructors
    pio.cpu = cpu.CPU()
    pio.storage = FileStore.FileStore()
    pio.server = VFP.VfpServer()
    pio.storage.begin()
    pio.server.begin(0)
    
    # Initialize custom simulation modules
    gpio_simulation.setup_gpio()
    system_config.initialize_system()

def peripheral_loop():
    """Proteus peripheral polling loop"""
    pio.server.poll()
    gpio_simulation.update_leds()
    button_monitor.check_buttons()

# ============================================================================
# MAIN APPLICATION LOOP
# ============================================================================

def main():
    """Main function"""
    print("Proteus RPI3 Machine Maintenance Simulation")
    print("=" * 50)
    
    # Setup
    peripheral_setup()
    
    # Start button monitoring thread
    button_monitor.start_monitoring()
    
    # Start Flask API server thread
    api_server.start_flask_server()
    
    # Infinite loop
    while True:
        peripheral_loop()
        time.sleep(0.01)  # 10ms update rate

# ============================================================================
# COMMAND LINE EXECUTION
# ============================================================================

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutdown triggered")
        gpio_simulation.cleanup_gpio()

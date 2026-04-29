# Proteus Simulation Guide - Machine Maintenance System

## Overview

This guide explains how to adapt your Raspberry Pi GPIO code to run in Proteus circuit simulator. The code has been refactored into modular components that simulate hardware behavior while maintaining the Flask API endpoints.

## Files Created

### Core Simulation Files
1. **proteus_main.py** - Main entry point for Proteus simulation
2. **system_config.py** - Global configuration and state management
3. **gpio_simulation.py** - LED and relay control simulation
4. **button_monitor.py** - Button press and sensor input monitoring
5. **api_server.py** - Flask API endpoints (REST interface)

### Alternative
- **main_proteus.py** - Complete standalone version (all-in-one file)

## Architecture

```
Proteus Simulation Structure:
┌─────────────────────────────────────┐
│      proteus_main.py                │
│   (Proteus entry point)             │
├─────────────────────────────────────┤
│                                     │
├─ system_config.py      ────────────┤ Global state, configuration
│                                     │
├─ gpio_simulation.py    ────────────┤ LED/relay control
│                                     │
├─ button_monitor.py     ────────────┤ Button input, state logic
│                                     │
├─ api_server.py         ────────────┤ Flask REST endpoints
│                                     │
└─────────────────────────────────────┘
```

## Key Differences from Raspberry Pi Code

### 1. **No Hardware Dependencies**
- ❌ Removed: `RPi.GPIO`, `RPLCD` (hardware-specific)
- ✅ Added: Virtual GPIO simulation, console output

### 2. **Simplified Input/Output**
- **GPIO Setup**: No actual pin configuration needed
- **LED Control**: Simulated with console output (colored text)
- **Button Input**: Simulated (can be automated or manual)
- **Sensor Input**: Simulated with state variables

### 3. **Console Output**
All operations logged to console with timestamps and status indicators:
```
[GPIO SETUP] Initializing pins...
[GPIO ON ] LED_DOWNTIME (GPIO 26)
[BUTTON] Maintenance pressed
[MAINTENANCE] Event started
```

## Pin Mapping

All GPIO pin numbers remain the same:

| Type | Component | GPIO | Status |
|------|-----------|------|--------|
| **LED** | Downtime | 26 | Output |
| | Maintenance | 20 | Output |
| | Break | 16 | Output |
| | Downtime Alert | 7 | Output |
| | Cancel | 13 | Output |
| | System Reset | 17 | Output |
| **Button** | Material Change | 19 | Input |
| | Maintenance | 21 | Input |
| | Break | 12 | Input |
| | Cancel | 6 | Input |
| | System Reset | 27 | Input |
| | Power Cut | 8 | Input |
| **Sensor** | Obstacle | 1 | Input |
| **Relay** | Power | 22 | Output |

## Running the Simulation

### Option 1: Simple Modular Version (Recommended)
```bash
python proteus_main.py
```

### Option 2: All-in-One Version
```bash
python main_proteus.py
```

### Expected Output
```
==================================================
PROTEUS SIMULATION - Machine Maintenance System
==================================================

[INIT] Machine: PROTEUS_SIM
[INIT] Status: working
[INIT] Power: ON

[GPIO SETUP] Initializing pins...
[LED TEST] Turning on all LEDs for 2 seconds...

[MONITOR] Button monitoring active
Ready to receive simulated button presses

[API] Flask server starting on http://0.0.0.0:5001

==================================================
```

## API Endpoints

The simulation provides REST API endpoints on `http://localhost:5001`:

### Health Check
```bash
GET /health
```

### Get Status
```bash
GET /status
```
Response:
```json
{
  "machine_name": "PROTEUS_SIM",
  "status": "working",
  "power_on": true,
  "downtime_triggered": false
}
```

### Power Cut
```bash
POST /power_cut
Content-Type: application/json

{
  "machine_name": "PROTEUS_SIM"
}
```

### Power Restore
```bash
POST /power_restore
Content-Type: application/json

{
  "machine_name": "PROTEUS_SIM"
}
```

### System Reset
```bash
POST /reset
Content-Type: application/json

{
  "machine_name": "PROTEUS_SIM"
}
```

### API Documentation
```bash
GET /api/docs
```

## Simulating Button Presses

In Proteus, you would connect virtual buttons to GPIO inputs. For testing, the simulation supports:

1. **Manual Testing** - Modify button states in `button_monitor.py`:
```python
def simulate_button_press(button_name):
    """Simulate a button press"""
    pin = BUTTON_PINS.get(button_name)
    # Press and release button
```

2. **Automated Testing** - Create test scripts:
```python
from button_monitor import simulate_button_press
import time

# Simulate material change
simulate_button_press('CHANGING_MATERIAL')
time.sleep(1)

# Simulate maintenance
simulate_button_press('MAINTENANCE')
```

## Event Sequence Example

### Material Change Event
1. Press "Material Change" button
2. **Status**: `material_change_active = True`
3. **Timer**: 180-second countdown starts
4. **LED**: Downtime alert may activate after 180s
5. Press "Material Change" again or wait for timeout

### Maintenance Event
1. Press "Maintenance" button (requires downtime trigger first)
2. **State 1 - Started**: Waiting for technician to arrive
   - **LED_MAINTENANCE**: ON
3. Press "Maintenance" again (technician arrival)
2. **State 2 - Arrived**: Waiting for maintenance completion
   - **LED_MAINTENANCE**: BLINKING
4. Press "Maintenance" again (maintenance complete)
   - **LED_MAINTENANCE**: OFF, system resets

## Log Files

The simulation creates log files:
- **proteus_simulation.log** - All system events and errors
- **button_log.log** - Button and event history

View logs:
```bash
tail -f proteus_simulation.log
```

## Testing the REST API

### Using curl:
```bash
# Check status
curl http://localhost:5001/status

# Cut power
curl -X POST http://localhost:5001/power_cut \
  -H "Content-Type: application/json" \
  -d '{"machine_name": "PROTEUS_SIM"}'

# Restore power
curl -X POST http://localhost:5001/power_restore \
  -H "Content-Type: application/json" \
  -d '{"machine_name": "PROTEUS_SIM"}'
```

### Using Python requests:
```python
import requests

# Get status
response = requests.get('http://localhost:5001/status')
print(response.json())

# Cut power
response = requests.post('http://localhost:5001/power_cut',
    json={'machine_name': 'PROTEUS_SIM'})
print(response.json())
```

## Integration with Proteus Circuit Designer

When setting up your Proteus circuit:

1. **Add GPIO Simulator Block** (if available in your Proteus version)
2. **Connect Virtual Pins**:
   - Buttons to input pins (GPIO 6, 8, 12, 19, 21, 27)
   - Sensor to GPIO 1
   - LEDs to output pins (GPIO 7, 13, 16, 17, 20, 26)
   - Relay to GPIO 22

3. **Python Integration**:
   - Proteus can interface with Python via VFP (Virtual Firmware Platform)
   - The simulation reads/writes virtual GPIO states
   - JSON log files can be exported for analysis

## Customization

### Change Machine Name
Edit `system_config.py`:
```python
class SystemState:
    def __init__(self):
        self.team_name = "YOUR_MACHINE_NAME"
```

### Change Port
Edit `api_server.py`:
```python
app.run(host='0.0.0.0', port=5002)  # Changed from 5001
```

### Add Custom Events
Edit `button_monitor.py` and `api_server.py` to handle new events.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 5001 already in use | Change port in `api_server.py` |
| Flask not installing | `pip install flask` |
| No output | Check logs in `proteus_simulation.log` |
| Buttons not responsive | Verify pin numbers in `system_config.py` |

## Converting Back to Raspberry Pi

When ready to deploy to actual RPi:

1. Use `main_raspberrypi_original.py` (your original code)
2. Import real GPIO modules: `import RPi.GPIO as GPIO`
3. Replace simulation functions with actual hardware calls
4. Remove Flask endpoints if not needed on device
5. Test on physical Raspberry Pi 3

## Network Configuration for Real System

For actual deployment, configure:

```python
MAIN_API_BASE_URL = "http://<main_server_ip>:5000/api"
```

## Performance Notes

- **Polling Rate**: 10ms (0.01 second loops)
- **API Response Time**: < 100ms
- **Memory Usage**: < 50MB
- **CPU Usage**: < 5% on RPI3

## Future Enhancements

Potential additions for expanded simulation:
- [ ] GUI interface for button simulation
- [ ] Real-time LED state visualization
- [ ] Network traffic monitoring
- [ ] Performance metrics dashboard
- [ ] Automated test suite
- [ ] Event replay/analysis tools

## Support

For issues or questions:
1. Check `proteus_simulation.log` for error details
2. Review button press sequences in console output
3. Verify API endpoints with curl/postman
4. Ensure all modules are in same directory

---
**Last Updated**: April 2026
**Version**: 1.0 - Proteus Simulation

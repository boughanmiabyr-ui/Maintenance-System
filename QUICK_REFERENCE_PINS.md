# ⚡ Quick Reference - Proteus Pin Configuration

## 🎯 Why "Real Time Simulation Failed" Happens

```
❌ MISSING = Error:
   ├─ No virtual circuit in Proteus
   ├─ No GPIO components
   ├─ No python.exe configured
   └─ No pin labels

✅ SOLUTION = Add to your Proteus circuit:
   ├─ 6 LEDs (220Ω resistors)
   ├─ 6 Buttons (10kΩ pull-ups)
   ├─ 1 Sensor
   ├─ 1 Relay (with transistor)
   └─ Configure VSM with Python script
```

---

## 📌 Complete Pin Mapping (Copy This!)

### **OUTPUTS (GPIO → Component)**
```
GPIO 26 (Pin 37) → LED + 220Ω → GND  (LED_DOWNTIME)
GPIO 20 (Pin 38) → LED + 220Ω → GND  (LED_MAINTENANCE)
GPIO 16 (Pin 36) → LED + 220Ω → GND  (LED_BREAK)
GPIO 7  (Pin 26) → LED + 220Ω → GND  (LED_DOWNTIME_ALERT)
GPIO 13 (Pin 33) → LED + 220Ω → GND  (LED_CANCEL)
GPIO 17 (Pin 11) → LED + 220Ω → GND  (LED_SYSTEM_RESET)
GPIO 22 (Pin 15) → Relay/Buzzer      (RELAY_POWER)
```

### **INPUTS (Button/Sensor → GPIO)**
```
GPIO 19 (Pin 35) ← VCC via 10kΩ ← Button → GND  (BTN_MATERIAL)
GPIO 21 (Pin 40) ← VCC via 10kΩ ← Button → GND  (BTN_MAINTENANCE)
GPIO 12 (Pin 32) ← VCC via 10kΩ ← Button → GND  (BTN_BREAK)
GPIO 6  (Pin 31) ← VCC via 10kΩ ← Button → GND  (BTN_CANCEL)
GPIO 27 (Pin 13) ← VCC via 10kΩ ← Button → GND  (BTN_SYSTEM_RESET)
GPIO 8  (Pin 24) ← VCC via 10kΩ ← Button → GND  (BTN_POWER_CUT)
GPIO 1  (Pin ??) ← Sensor Output                (SENSOR_OBSTACLE)
```

---

## 🔧 3-Minute Setup Guide

### **Step 1: Add Components to Proteus**
```
1. Open Proteus (Circuit/VSM mode)
2. Add: 6× LED (pick any color)
3. Add: 6× Resistor 220Ω (for LEDs)
4. Add: 6× Resistor 10kΩ (for buttons)
5. Add: 6× Button/Switch
6. Add: 1× Sensor module
7. Add: 1× Relay or Buzzer
8. Add: 1× 2N2222 Transistor (for relay)
9. Add: 1× 1N4007 Diode (for relay protection)
10. Add: RPI or ATMEGA microcontroller
```

### **Step 2: Wire Components**
```
FOR EACH LED:
  GPIO → [220Ω] → LED+ → (LED-) → GND

FOR EACH BUTTON:
  VCC → [10kΩ] → GPIO ← Button → GND

FOR SENSOR:
  GPIO ← Sensor Output
  VCC → Sensor VCC
  GND → Sensor GND

FOR RELAY:
  GPIO → [1kΩ] → Transistor Base
  Transistor Collector → Relay Coil → GND
  Diode across relay coil
  Relay Output to Machine Power
```

### **Step 3: Configure Proteus**
```
1. Tools → Firmware Options
2. Select Microcontroller → RPI3
3. Point to: main_proteus.py
4. Python Executable: C:\Python3X\python.exe
5. Click OK
```

### **Step 4: Label Each Pin**
```
1. Right-click each GPIO connection
2. "Add Net Label"
3. Type: GPIO26, GPIO20, GPIO16, etc.
4. Save project
```

### **Step 5: Enable Python I/O in Code**

In `main_proteus.py`, uncomment these lines:
```python
# Line ~145: set_led()
def set_led(pin, state):
    if PROTEUS_MODE:
        gpio_value = 1 if state else 0
        pio.digitalwrite(pin, gpio_value)  # ← UNCOMMENT THIS

# Line ~155: read_button()
def read_button(pin):
    if PROTEUS_MODE:
        return pio.digitalread(pin)  # ← UNCOMMENT THIS

# Line ~165: read_sensor()
def read_sensor(pin):
    if PROTEUS_MODE:
        return pio.digitalread(pin)  # ← UNCOMMENT THIS
```

---

## 📊 Pin Summary Table

| GPIO | Type | Net Name | Component | Resistor | Logic |
|------|------|----------|-----------|----------|-------|
| 26 | OUT | GPIO26 | LED Red | 220Ω | HIGH=ON |
| 20 | OUT | GPIO20 | LED Yel | 220Ω | HIGH=ON |
| 16 | OUT | GPIO16 | LED Grn | 220Ω | HIGH=ON |
| 7 | OUT | GPIO7 | LED Yel | 220Ω | HIGH=ON |
| 13 | OUT | GPIO13 | LED Grn | 220Ω | HIGH=ON |
| 17 | OUT | GPIO17 | LED Blu | 220Ω | HIGH=ON |
| 22 | OUT | GPIO22 | Relay | 1kΩ | HIGH=ON |
| 19 | IN | GPIO19 | Button | 10kΩ | LOW=PRESS |
| 21 | IN | GPIO21 | Button | 10kΩ | LOW=PRESS |
| 12 | IN | GPIO12 | Button | 10kΩ | LOW=PRESS |
| 6 | IN | GPIO6 | Button | 10kΩ | LOW=PRESS |
| 27 | IN | GPIO27 | Button | 10kΩ | LOW=PRESS |
| 8 | IN | GPIO8 | Button | 10kΩ | LOW=PRESS |
| 1 | IN | GPIO1 | Sensor | - | LOW=DET |

---

## ✨ Simple Component List

**You need exactly this:**
```
6× LED (any color)
6× Resistor 220Ω (for LEDs)
6× Resistor 10kΩ (for buttons)
6× Push Button
1× Digital Sensor (IR/PIR/Switch)
1× Relay (5V or 12V)
1× Transistor 2N2222 (NPN)
1× Diode 1N4007
1× Resistor 1kΩ (for transistor)
1× Microcontroller (RPI or ATMEGA)
1× Power Supply (5V)
1× Ground rail

TOTAL: Very simple circuit! ~$10-15 in parts
```

---

## 🎨 Visual Pin Layout

```
RPI GPIO Position (Top View):

3.3V │ 5V │
─────┼────┤
 2   │ 3  │  (I2C - not used)
─────┼────┤
 4   │    │  
─────┼────┤
 17  │ 27 │  ← BUTTON_SYSTEM_RESET
─────┼────┤
 22  │    │  ← RELAY_POWER
─────┼────┤
 23  │ 24 │
─────┼────┤
 25  │ 8  │  ← BUTTON_POWER_CUT
─────┼────┤
 7   │11  │  ← LED_DOWNTIME_ALERT, LED_SYSTEM_RESET
─────┼────┤
 5   │ 6  │  ← BUTTON_CANCEL
─────┼────┤
 12  │ 13 │  ← BUTTON_BREAK, LED_CANCEL
─────┼────┤
 26  │ 19 │  ← LED_DOWNTIME, BUTTON_MATERIAL
─────┼────┤
 16  │ 20 │  ← LED_BREAK, LED_MAINTENANCE
─────┼────┤
 21  │    │  ← BUTTON_MAINTENANCE
─────┼────┤
 1   │    │  ← SENSOR_OBSTACLE
─────┼────┤
GND  │    │
```

---

## 🧪 Test Script

```python
# Quick test - add to main_proteus.py

def test_all_pins():
    """Test all GPIO pins"""
    print("\n[TEST] Starting pin test...\n")
    
    # Test all LEDs
    print("Testing LEDs...")
    for pin in [26, 20, 16, 7, 13, 17]:
        set_led(pin, True)
        time.sleep(0.3)
    for pin in [26, 20, 16, 7, 13, 17]:
        set_led(pin, False)
    
    # Test relay
    print("Testing Relay...")
    set_relay(22, True)
    time.sleep(1)
    set_relay(22, False)
    
    print("\n[TEST] All pins tested successfully!\n")

# Call in main():
# test_all_pins()
```

---

## 🔍 Debugging Checklist

If simulation still fails:

- [ ] Proteus: File → Open VSM (simulation mode)
- [ ] Added all components to circuit?
- [ ] Wired all GPIO pins?
- [ ] Labeled all net names (GPIO26, GPIO20, etc.)?
- [ ] Configured VSM with python.exe path?
- [ ] Uncommented pio.digitalread/write lines?
- [ ] Python 3.7+ installed?
- [ ] Flask installed? (`pip install flask`)
- [ ] main_proteus.py in correct folder?
- [ ] All resistor values correct?

---

## 🚀 Expected Output When Running

```
============================================================
PROTEUS SIMULATION - Machine Maintenance System
============================================================

[INIT] Machine: PROTEUS_SIMULATION
[INIT] Status: working
[INIT] Power: ON

[GPIO SETUP] Initializing pins...
[GPIO 26] LED: ON
[GPIO 20] LED: ON
[GPIO 16] LED: ON
[GPIO 7] LED: ON
[GPIO 13] LED: ON
[GPIO 17] LED: ON
[LED TEST] All on for 2 seconds...
[GPIO 26] LED: OFF
[GPIO 20] LED: OFF
...
[MONITOR] Waiting for button/sensor inputs...
[API] Flask server starting on http://0.0.0.0:5001

Ready!
(Now press buttons in Proteus circuit)
```

---

## ❓ FAQ

**Q: Can I use buzzers instead of relay?**
A: Yes! Connect GPIO22 → 220Ω → Buzzer+ → 5V, Buzzer- → GND

**Q: What if I don't have exact resistor values?**
A: Use closest: 200-240Ω for LEDs, 8-12kΩ for pull-ups

**Q: How do I test without buttons?**
A: Uncomment test_all_pins() in main_proteus.py

**Q: Can I use Arduino instead of RPI?**
A: Yes! Use ATMEGA328 in Proteus, same GPIO pins work

**Q: How do I send data to main system?**
A: The Flask API on port 5001 handles this automatically

---

## 📞 Still Not Working?

Check these files for detailed help:
- `PROTEUS_PIN_MAPPING_GUIDE.md` - Full setup guide
- `PROTEUS_CIRCUIT_DIAGRAMS.md` - All circuit diagrams
- `main_proteus.py` - Python code with comments

**Your single file:** `main_proteus.py` - Everything is here!

---

**That's it! Your Proteus simulation is ready.** ✅

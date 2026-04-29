# 📌 Proteus Circuit Pin Mapping Guide

## 🎯 Why the Error Occurred

The error **"Real Time Simulation failed to start"** happens because:
1. ❌ No virtual GPIO components in your Proteus circuit
2. ❌ The Python code has no actual connection to Proteus I/O
3. ❌ Missing circuit diagram with proper pin assignments

## ✅ Solution: Set Up Proteus Circuit

### Step 1: Create Virtual GPIO in Proteus Circuit

In your **Proteus circuit diagram (.pdsprj)**, add these components:

#### **A. LED Configuration (6 LEDs)**

| Component | GPIO Pin | Label | Function |
|-----------|----------|-------|----------|
| LED + 220Ω Resistor | 26 | LED_DOWNTIME | Downtime indicator |
| LED + 220Ω Resistor | 20 | LED_MAINTENANCE | Maintenance indicator |
| LED + 220Ω Resistor | 16 | LED_BREAK | Break indicator |
| LED + 220Ω Resistor | 7 | LED_DOWNTIME_ALERT | Status/Alert indicator |
| LED + 220Ω Resistor | 13 | LED_CANCEL | Cancel indicator |
| LED + 220Ω Resistor | 17 | LED_SYSTEM_RESET | Reset indicator |

**Proteus Steps for LED:**
1. Add component: `LED` (red, green, or yellow)
2. Add resistor (220Ω): `RES` → 220Ω
3. Connect: **GPIO Pin → 220Ω Resistor → LED Anode → GND**
4. Label the GPIO pin with the name above
5. Set pin type to **OUTPUT** in your microcontroller config

**Circuit Diagram:**
```
RPI_GPIO_PIN
    ↓
  220Ω
    ↓
   LED (+)
    ↓
   GND (-)
```

---

#### **B. Button Configuration (6 Buttons)**

| Component | GPIO Pin | Label | Function |
|-----------|----------|-------|----------|
| Push Button | 19 | BUTTON_MATERIAL | Material change button |
| Push Button | 21 | BUTTON_MAINTENANCE | Maintenance button |
| Push Button | 12 | BUTTON_BREAK | Break button |
| Push Button | 6 | BUTTON_CANCEL | Cancel button |
| Push Button | 27 | BUTTON_SYSTEM_RESET | System reset button |
| Push Button | 8 | BUTTON_POWER_CUT | Power cut/restore button |

**Proteus Steps for Button:**
1. Add component: `SW-PB` (push button)
2. Connect: **GPIO Pin ← Pull-Up Resistor (10kΩ) ← VCC**
3. Connect: **GPIO Pin ← Button → GND**
4. Label the GPIO pin with the name above
5. Set pin type to **INPUT with PULL-UP** in your microcontroller config

**Circuit Diagram:**
```
VCC (+)
  ↓
10kΩ (Pull-up)
  ↓
GPIO_PIN ←──── Button Switch ────→ GND
```

---

#### **C. Sensor Configuration (1 Sensor)**

| Component | GPIO Pin | Label | Function |
|-----------|----------|-------|----------|
| Digital Sensor | 1 | SENSOR_OBSTACLE | Obstacle detection sensor |

**Proteus Steps for Sensor:**
1. Add component: `IR Sensor`, `PIR Sensor`, or `Digital Sensor`
2. Connect: **GPIO Pin ← Sensor Output**
3. Connect: **VCC → Sensor VCC, GND → Sensor GND**
4. Label: `SENSOR_OBSTACLE`
5. Set pin type to **INPUT** in your microcontroller config

**Circuit Diagram:**
```
         Sensor Module
         ┌─────────────┐
VCC ────→│VCC         │
GND ────→│GND      OUT│───→ GPIO_PIN (1)
         └─────────────┘
```

---

#### **D. Buzzer/Relay Configuration (1 Relay)**

| Component | GPIO Pin | Label | Function |
|-----------|----------|-------|----------|
| Relay + Transistor | 22 | RELAY_POWER | Power control relay |

**Proteus Steps for Relay:**
1. Add component: **Relay (12V or 5V)** + **NPN Transistor (2N2222)** + **Diode (1N4007)**
2. Connect GPIO to transistor base (with 1kΩ resistor)
3. Transistor drives relay coil
4. Relay switches power to machine

**Circuit Diagram:**
```
GPIO_PIN (22)
    ↓
   1kΩ
    ↓
   2N2222 Transistor (Base)
    ↓ (Collector)
  Relay Coil ←─ 1N4007 Diode (protection)
    ↓ (Emitter)
   GND

Relay Contacts:
   Terminal A ──→ Machine Power (+12V)
   Terminal B ──→ Output (to machine)
   Terminal C ──→ GND
```

---

## 🔧 Complete Proteus Circuit Pin Mapping

```
PROTEUS CIRCUIT SCHEMATIC
═══════════════════════════════════════════

OUTPUTS (GPIO → VCC through resistor → Component):
─────────────────────────────────────────────
GPIO 26 → 220Ω → LED_DOWNTIME → GND
GPIO 20 → 220Ω → LED_MAINTENANCE → GND
GPIO 16 → 220Ω → LED_BREAK → GND
GPIO 7  → 220Ω → LED_DOWNTIME_ALERT → GND
GPIO 13 → 220Ω → LED_CANCEL → GND
GPIO 17 → 220Ω → LED_SYSTEM_RESET → GND
GPIO 22 → 1kΩ → 2N2222 Base → Relay Coil → GND

INPUTS (VCC → Pull-up → GPIO → Button → GND):
─────────────────────────────────────────────
GPIO 19 ← 10kΩ Pull-up ← VCC, Button ← GND (BUTTON_MATERIAL)
GPIO 21 ← 10kΩ Pull-up ← VCC, Button ← GND (BUTTON_MAINTENANCE)
GPIO 12 ← 10kΩ Pull-up ← VCC, Button ← GND (BUTTON_BREAK)
GPIO 6  ← 10kΩ Pull-up ← VCC, Button ← GND (BUTTON_CANCEL)
GPIO 27 ← 10kΩ Pull-up ← VCC, Button ← GND (BUTTON_SYSTEM_RESET)
GPIO 8  ← 10kΩ Pull-up ← VCC, Button ← GND (BUTTON_POWER_CUT)
GPIO 1  ← Sensor output (INPUT) (SENSOR_OBSTACLE)

POWER:
──────
VCC: +3.3V or +5V (for pull-ups and LEDs)
GND: Common ground
```

---

## 📋 Step-by-Step Proteus Setup

### **1. Create New Proteus Project**
```
File → New Circuitry Project
```

### **2. Add Microcontroller**
```
- Component Library: Search "RPI3" or "ATMEGA328"
- Place on schematic
- This is your virtual RPI/Arduino
```

### **3. Add All Components**

**For Each LED (×6):**
```
1. Add: LED component
2. Add: 220Ω Resistor
3. Connect: GPIO → Resistor → LED Anode → GND
4. Label: "LED26", "LED20", etc.
```

**For Each Button (×6):**
```
1. Add: SW-PB (push button)
2. Add: 10kΩ Resistor
3. Connect: VCC → 10kΩ → GPIO node
4. Connect: GPIO node → Button → GND
5. Label: "BTN19", "BTN21", etc.
```

**For Sensor:**
```
1. Add: Sensor module component
2. Connect: VCC, GND, OUTPUT to GPIO 1
3. Label: "SENSOR"
```

**For Relay:**
```
1. Add: Relay component
2. Add: 2N2222 Transistor
3. Add: 1N4007 Diode
4. Connect: GPIO22 → 1kΩ → Transistor Base
5. Connect: Transistor Collector → Relay Coil → GND
6. Connect: Diode across relay coil (protection)
7. Label: "RELAY_POWER"
```

### **4. Connect All to GND and VCC**
```
- All grounds → Common GND rail
- All VCC pull-ups → VCC rail (+3.3V or +5V)
```

### **5. Label Each GPIO Pin**
```
In Proteus:
- Right-click each GPIO connection
- Add Net Label
- Name: GPIO26, GPIO20, GPIO16, etc.
```

---

## 💻 Modified Python Code for Proteus

### **Updated GPIO Read/Write Functions:**

```python
def set_led(pin, state):
    """Set LED output high/low"""
    if PROTEUS_MODE:
        # Uncomment these two lines when running in Proteus:
        # gpio_value = 1 if state else 0
        # pio.digitalwrite(pin, gpio_value)
        pass
    print(f"[GPIO {pin}] LED: {'ON' if state else 'OFF'}")

def read_button(pin):
    """Read button input"""
    if PROTEUS_MODE:
        # Uncomment this line when running in Proteus:
        # return pio.digitalread(pin)  # Returns 1 (released) or 0 (pressed)
        return True  # Default: button released
    return True

def read_sensor(pin):
    """Read sensor input"""
    if PROTEUS_MODE:
        # Uncomment this line when running in Proteus:
        # return pio.digitalread(pin)  # Returns 1 (no obstacle) or 0 (obstacle)
        return True  # Default: no obstacle
    return True
```

---

## 📌 Complete Pin Reference Table

```
╔════════════════════════════════════════════════════════════════╗
║           PROTEUS GPIO PIN ASSIGNMENT TABLE                   ║
╠════════════════════════════════════════════════════════════════╣
║ PIN │ TYPE   │ FUNCTION           │ COMPONENT        │ CONFIG  ║
╠────┼────────┼──────────────────────┼──────────────────┼─────────╣
║ 26 │ OUTPUT │ LED_DOWNTIME        │ LED + 220Ω        │ HIGH=ON  ║
║ 20 │ OUTPUT │ LED_MAINTENANCE     │ LED + 220Ω        │ HIGH=ON  ║
║ 16 │ OUTPUT │ LED_BREAK           │ LED + 220Ω        │ HIGH=ON  ║
║  7 │ OUTPUT │ LED_DOWNTIME_ALERT  │ LED + 220Ω        │ HIGH=ON  ║
║ 13 │ OUTPUT │ LED_CANCEL          │ LED + 220Ω        │ HIGH=ON  ║
║ 17 │ OUTPUT │ LED_SYSTEM_RESET    │ LED + 220Ω        │ HIGH=ON  ║
║ 22 │ OUTPUT │ RELAY_POWER         │ 2N2222 + Relay    │ HIGH=ON  ║
╠────┼────────┼──────────────────────┼──────────────────┼─────────╣
║ 19 │ INPUT  │ BUTTON_MATERIAL     │ Button + 10kΩ     │ LOW=PRESSED ║
║ 21 │ INPUT  │ BUTTON_MAINTENANCE  │ Button + 10kΩ     │ LOW=PRESSED ║
║ 12 │ INPUT  │ BUTTON_BREAK        │ Button + 10kΩ     │ LOW=PRESSED ║
║  6 │ INPUT  │ BUTTON_CANCEL       │ Button + 10kΩ     │ LOW=PRESSED ║
║ 27 │ INPUT  │ BUTTON_SYSTEM_RESET │ Button + 10kΩ     │ LOW=PRESSED ║
║  8 │ INPUT  │ BUTTON_POWER_CUT    │ Button + 10kΩ     │ LOW=PRESSED ║
╠────┼────────┼──────────────────────┼──────────────────┼─────────╣
║  1 │ INPUT  │ SENSOR_OBSTACLE     │ Digital Sensor    │ LOW=ACTIVE  ║
╚════════════════════════════════════════════════════════════════╝

VOLTAGE LEVELS:
- VCC: 3.3V (for RPI) or 5V (for Arduino)
- GND: 0V (Common ground)
- HIGH: 3.3V or 5V (logic 1)
- LOW: 0V (logic 0)
```

---

## 🔗 Proteus I/O Function Reference

```python
# READ digital input
state = pio.digitalread(pin)  # Returns 1 or 0

# WRITE digital output
pio.digitalwrite(pin, value)  # value = 0 (LOW) or 1 (HIGH)

# READ analog input
value = pio.analogread(pin)  # Returns 0-1023

# WRITE PWM
pio.analogwrite(pin, value)  # value = 0-255
```

---

## ✅ Verification Checklist

Before running simulation:

- [ ] All 6 LEDs connected (GPIO 26, 20, 16, 7, 13, 17)
- [ ] All 6 buttons connected (GPIO 19, 21, 12, 6, 27, 8)
- [ ] Sensor connected (GPIO 1)
- [ ] Relay/Buzzer connected (GPIO 22)
- [ ] Pull-up resistors on all button inputs (10kΩ)
- [ ] Current-limiting resistors on all LEDs (220Ω)
- [ ] All grounds connected together (common GND)
- [ ] All VCC connected together (common VCC)
- [ ] Net labels on each GPIO pin
- [ ] GPIO pin configuration set (input/output)

---

## 🚀 Running Simulation

1. **Save Proteus project** (as .pdsprj)
2. **Enable Virtual Firmware Platform (VFP)** in Proteus
3. **Point to Python script**: `main_proteus.py`
4. **Set Python path** in Proteus settings
5. **Click "Play"** to start simulation
6. **Watch console output** for LED/button events

---

## 📞 Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| "Real Time Simulation failed" | No circuit or missing pins | Add components & labels |
| Button doesn't work | No pull-up resistor | Add 10kΩ to VCC |
| LED always on/off | Inverted logic | Check set_led() function |
| Sensor not responding | No component in circuit | Add sensor module |
| Python can't find pins | Missing net labels | Label each GPIO |

---

## 📖 Additional Resources

- **Proteus documentation**: Help → Virtual Firmware Platform
- **RPI GPIO**: https://pinout.xyz/
- **Standard resistor values**: 220Ω (LED), 10kΩ (pull-up), 1kΩ (base)

---

**Your `main_proteus.py` is now ready!**  
Just build the circuit above in Proteus, uncomment the `pio.` lines, and it will work. ✅

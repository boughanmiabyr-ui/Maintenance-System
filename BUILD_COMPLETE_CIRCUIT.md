# 🎨 Complete Proteus Circuit Example

## How to Build This in Proteus

### **What You'll Create:**
A working Proteus circuit with 14 GPIO pins connected to:
- 6 LEDs (with resistors)
- 6 Buttons (with pull-ups)
- 1 Sensor
- 1 Relay

---

## Step-by-Step Build Instructions

### **STEP 1: Create New Project**
```
File → New → Circuitry Project
Save as: "simulation.pdsprj"
```

### **STEP 2: Add Microcontroller**
```
1. Click "Choose a device" or "Add Component"
2. Search: "RPI3" or "ATMEGA328P"
3. Click RPI3
4. Place on schematic (center area)
5. You now have your microcontroller
```

### **STEP 3: Add Power Rails**
```
1. Add component: "BAT" (Battery)
2. Set voltage: 5.0V
3. Add component: "GND" (Ground)
4. Connect Battery+ to power rail
5. Connect Battery- and GND to ground rail
6. Your circuit now has power
```

### **STEP 4: Add All LEDs (×6)**

**For LED #1 (GPIO 26):**
```
1. Add component: LED (RED)
   - Library: Device → Optoelectronics → LED

2. Add component: RES (Resistor)
   - Value: 220Ω
   - Library: Device → Resistors

3. Wire:
   GPIO26 ──→ 220Ω Resistor ──→ LED Anode (+) ┐
                                               │
   GND ←──────────────────── LED Cathode (-) ┘

4. Right-click GPIO26 connection
5. Select "Add Net Label"
6. Type: "GPIO26"
7. Check label appears
```

**Repeat for LED #2-6:**
- GPIO 20 → 220Ω → LED (yellow)
- GPIO 16 → 220Ω → LED (green)
- GPIO 7 → 220Ω → LED (yellow)
- GPIO 13 → 220Ω → LED (green)
- GPIO 17 → 220Ω → LED (blue)

**Label each GPIO: GPIO26, GPIO20, GPIO16, GPIO7, GPIO13, GPIO17**

---

### **STEP 5: Add All Buttons (×6)**

**For Button #1 (GPIO 19):**
```
1. Add component: SW-PB (Push Button)
   - Library: Device → Switches

2. Add component: RES (Resistor)
   - Value: 10kΩ
   - Library: Device → Resistors

3. Wire:
   VCC (+5V) ────────┬────→ GPIO19
                     │
                   10kΩ (Pull-up resistor)
                     │
   Button Switch ────┤
                     │
   GND ──────────────┘

4. Right-click GPIO19 connection
5. Select "Add Net Label"
6. Type: "GPIO19"
```

**Repeat for Button #2-6:**
- VCC → 10kΩ → GPIO21 ← Button → GND
- VCC → 10kΩ → GPIO12 ← Button → GND
- VCC → 10kΩ → GPIO6 ← Button → GND
- VCC → 10kΩ → GPIO27 ← Button → GND
- VCC → 10kΩ → GPIO8 ← Button → GND

**Label each GPIO: GPIO19, GPIO21, GPIO12, GPIO6, GPIO27, GPIO8**

---

### **STEP 6: Add Sensor (×1)**

**For Sensor (GPIO 1):**
```
1. Add component: "SEN" or "SENSOR"
   - Or use: SW-PB as simulation
   - Library: Device → Sensors (if available)

2. Connect:
   Sensor VCC ────→ +5V
   Sensor GND ────→ GND
   Sensor OUT ────→ GPIO1

3. Right-click GPIO1 connection
4. Select "Add Net Label"
5. Type: "GPIO1"
```

---

### **STEP 7: Add Relay Control (×1)**

**For Relay (GPIO 22):**
```
1. Add component: RELAY
   - Library: Device → Relays

2. Add component: Q2N2222 (NPN Transistor)
   - Library: Device → Transistors

3. Add component: D1N4007 (Diode)
   - Library: Device → Diodes

4. Add component: RES (1kΩ)
   - Library: Device → Resistors

5. Wire:
   GPIO22 ──→ 1kΩ ──→ Base (B) of 2N2222
   
   Collector (C) ─→ Relay Coil ─→ Back to GND
   
   Emitter (E) ──→ GND
   
   Diode 1N4007:
   (Anode +) ──→ Relay Coil
   (Cathode -) ← From GND side of relay
   (Protection across relay coil)

6. Right-click GPIO22 connection
7. Select "Add Net Label"
8. Type: "GPIO22"
```

---

### **STEP 8: Connect All to Power**

```
All 10kΩ pull-ups (6 buttons) ──→ VCC Rail
All LED 220Ω resistors ──→ From GPIO pins
All LED cathodes ──→ GND Rail
Sensor VCC ──→ VCC Rail
Sensor GND ──→ GND Rail
Relay coil ──→ Transistor
Transistor emitter ──→ GND Rail
```

---

### **STEP 9: Verify All Connections**

Check that:
- [ ] GPIO26 labeled ✓
- [ ] GPIO20 labeled ✓
- [ ] GPIO16 labeled ✓
- [ ] GPIO7 labeled ✓
- [ ] GPIO13 labeled ✓
- [ ] GPIO17 labeled ✓
- [ ] GPIO22 labeled ✓
- [ ] GPIO19 labeled ✓
- [ ] GPIO21 labeled ✓
- [ ] GPIO12 labeled ✓
- [ ] GPIO6 labeled ✓
- [ ] GPIO27 labeled ✓
- [ ] GPIO8 labeled ✓
- [ ] GPIO1 labeled ✓
- [ ] All LEDs have resistors ✓
- [ ] All buttons have pull-ups ✓
- [ ] No floating wires ✓
- [ ] No short circuits ✓

---

### **STEP 10: Configure Virtual Firmware**

```
1. Go to: Tools → VSM Options (or Firmware)

2. In "Virtual Firmware Platform":
   - Microcontroller: RPI3
   - Clock: 32 MHz (default)
   - Program File: (leave blank or auto)

3. In "Python" section:
   - Enable: ☑ Python Support
   - Python Executable: C:\Python39\python.exe
   - Working Directory: C:\Users\Arij\Desktop\appstage2026PFE-main\
   - Script: main_proteus.py

4. Click OK
```

---

### **STEP 11: Save & Test**

```
1. File → Save As
   - Filename: "simulation.pdsprj"
   - Save in your project folder

2. Press Play button (▶️) in Proteus
3. You should see:
   - Python loading
   - LEDs testing (2 seconds on)
   - Flask server starting
   - "Ready for inputs"

4. Test each button in Proteus by clicking it
5. Watch console for:
   [BUTTON] Maintenance pressed
   [BUTTON] Break pressed
   etc.
```

---

## 📋 Complete Wiring Checklist

```
MICROCONTROLLER:
☐ RPI3 or ATMEGA328 placed on schematic
☐ VCC connected to +5V rail
☐ GND connected to GND rail

POWER SUPPLY:
☐ +5V battery/supply
☐ GND connection
☐ VCC rail (all +5V)
☐ GND rail (all GND)

LEDS (×6):
☐ GPIO26 → 220Ω → RED LED → GND, labeled "GPIO26"
☐ GPIO20 → 220Ω → YEL LED → GND, labeled "GPIO20"
☐ GPIO16 → 220Ω → GRN LED → GND, labeled "GPIO16"
☐ GPIO7 → 220Ω → YEL LED → GND, labeled "GPIO7"
☐ GPIO13 → 220Ω → GRN LED → GND, labeled "GPIO13"
☐ GPIO17 → 220Ω → BLU LED → GND, labeled "GPIO17"

BUTTONS (×6):
☐ GPIO19 ← VCC via 10kΩ ← Button → GND, labeled "GPIO19"
☐ GPIO21 ← VCC via 10kΩ ← Button → GND, labeled "GPIO21"
☐ GPIO12 ← VCC via 10kΩ ← Button → GND, labeled "GPIO12"
☐ GPIO6 ← VCC via 10kΩ ← Button → GND, labeled "GPIO6"
☐ GPIO27 ← VCC via 10kΩ ← Button → GND, labeled "GPIO27"
☐ GPIO8 ← VCC via 10kΩ ← Button → GND, labeled "GPIO8"

SENSOR:
☐ Sensor VCC → +5V
☐ Sensor GND → GND
☐ Sensor OUT → GPIO1, labeled "GPIO1"

RELAY/BUZZER:
☐ GPIO22 → 1kΩ → Transistor Base, labeled "GPIO22"
☐ Transistor Collector → Relay Coil
☐ Transistor Emitter → GND
☐ Diode 1N4007 across relay coil (protection)
☐ Relay output ready for machine power

CONFIGURATION:
☐ Proteus VSM set to RPI3
☐ Python path configured
☐ main_proteus.py pointed
☐ Project saved

CLEANUP:
☐ No floating wires
☐ No unconnected pins
☐ All labels visible
☐ No obvious short circuits
```

---

## 🧪 Testing Your Circuit

### **Test 1: Visual Check**
```
After clicking Play, you should see:
- LEDs 26, 20, 16, 7, 13, 17 light up for 2 seconds
- All go off
- Only LED 7 (downtime alert) stays on
- Flask server starts
```

### **Test 2: Button Test**
```
1. Click on Button (GPIO 19) in Proteus
2. Look at Python console
3. Should see: [BUTTON] Material Change pressed
```

### **Test 3: LED Test**
```
In Python console, manually run:
set_led(26, True)   → LED26 should light
set_led(26, False)  → LED26 should turn off
```

### **Test 4: API Test**
```
In another terminal:
python test_proteus_simulation.py

Should show all tests passing
```

---

## 📸 Expected Circuit Layout

```
┌────────────────────────────────────────────────────────┐
│                     PROTEUS CIRCUIT                     │
├────────────────────────────────────────────────────────┤
│                                                         │
│          VCC (+5V) Rail                                │
│                │                                       │
│   ┌────────────┴─────────────┬────────────┐           │
│   │                          │            │           │
│ [10kΩ]×6               [220Ω]×6      Relay Coil       │
│   │                          │            │           │
│   ├→ GPIO19          GPIO26 →│→LED →     TR Base      │
│   ├→ GPIO21          GPIO20 →│→LED →     (1kΩ)       │
│   ├→ GPIO12          GPIO16 →│→LED →                  │
│   ├→ GPIO6           GPIO7  →│→LED →     GPIO22       │
│   ├→ GPIO27          GPIO13 →│→LED →                  │
│   └→ GPIO8           GPIO17 →│→LED →    Transistor    │
│                              │          2N2222        │
│  ┌→ Button→GND (×6) All LED Cathodes→GND│           │
│  │                                     Diode          │
│  │ Sensor→GPIO1                       1N4007          │
│  │                                       │            │
│  │         RPI3                         GND           │
│  │     (Microcontroller)                              │
│  │                                                     │
│  └─────────────────────→ GND Rail                     │
│                          │                            │
│                        Battery-                       │
│                         (GND)                         │
└────────────────────────────────────────────────────────┘
```

---

## 🚀 Next Steps

1. **Build Circuit** - Follow steps 1-11 above
2. **Save Project** - File → Save
3. **Run Simulation** - Press Play (▶️)
4. **Test Buttons** - Click them in Proteus
5. **Check Console** - See button press messages
6. **Test LEDs** - Use Python commands
7. **Final API Test** - Run test suite

**All done! Your circuit is simulation-ready.** ✅

---

## ❓ Common Issues

| Issue | Fix |
|-------|-----|
| "No device found" | Did you download components? |
| "GPIO undefined" | Check all labels are correct |
| "Button doesn't work" | Missing 10kΩ pull-up resistor |
| "LED doesn't light" | Check 220Ω resistor direction |
| "Relay won't click" | Check transistor connections |
| Python won't load | Path to python.exe wrong |

---

**You now have everything needed to build a working Proteus simulation!** 🎉

# 🔌 Proteus Circuit Wiring Diagrams

## Complete Circuit Layout

```
═══════════════════════════════════════════════════════════════════════════
                    PROTEUS CIRCUIT - MACHINE MAINTENANCE
═══════════════════════════════════════════════════════════════════════════

                              POWER SUPPLY
                              ┌─────────────┐
                          +5V │             │ GND
                            ┌─┼─────────────┼─┐
                            │ │             │ │
                        VCC │ │             │ GND
                            │ │             │ │
                        ────┼─┘             └─┼────
                            │                 │
```

---

## 1️⃣  LED Outputs (×6)

### **LED 1: GPIO 26 (LED_DOWNTIME)**
```
GPIO26  (RPI pin 26)
   │
   ├─── 220Ω Resistor ───┬──→ LED Anode (+) →│→ LED Cathode (-)
   │                      │
   │                      └─→ GND
```

### **Generic LED Connection (All 6 LEDs Same)**
```
VCC Rail (+5V)
              
GPIO_PIN ──┬──[220Ω]──→ │→ LED  ──→ GND
           │ (Current    │→      
           │ Limiting)   │← Anode/Cathode
           │
         Output
```

**All 6 LEDs:**
- GPIO 26 → 220Ω → LED (RED) → GND
- GPIO 20 → 220Ω → LED (YELLOW) → GND
- GPIO 16 → 220Ω → LED (GREEN) → GND
- GPIO 7 → 220Ω → LED (YELLOW) → GND
- GPIO 13 → 220Ω → LED (GREEN) → GND
- GPIO 17 → 220Ω → LED (BLUE) → GND

---

## 2️⃣  Button Inputs (×6)

### **Button 1: GPIO 19 (BUTTON_CHANGING_MATERIAL)**
```
VCC (+5V)
   │
   ├──[10kΩ]──┬─→ GPIO19 (Input)
   │          │
   │        Button
   │          │
   └──────────┴─→ GND
   
When button pressed:
GPIO19 reads LOW (0) → Button activated
```

### **Generic Button Connection (All 6 Buttons Same)**
```
VCC Rail (+5V)
   │
   ├──[10kΩ]──┬─→ GPIO_PIN (Input)
   │          │
   │        Push Button (Momentary)
   │          │
   └──────────┴─→ GND Rail

State:
- Released (open) → GPIO reads HIGH (1) - Button not pressed
- Pressed (closed) → GPIO reads LOW (0) - Button pressed
```

**All 6 Buttons:**
- GPIO 19 ← 10kΩ ← VCC, Button → GND  (BUTTON_MATERIAL)
- GPIO 21 ← 10kΩ ← VCC, Button → GND  (BUTTON_MAINTENANCE)
- GPIO 12 ← 10kΩ ← VCC, Button → GND  (BUTTON_BREAK)
- GPIO 6 ← 10kΩ ← VCC, Button → GND   (BUTTON_CANCEL)
- GPIO 27 ← 10kΩ ← VCC, Button → GND  (BUTTON_SYSTEM_RESET)
- GPIO 8 ← 10kΩ ← VCC, Button → GND   (BUTTON_POWER_CUT)

---

## 3️⃣  Sensor Input (×1)

### **GPIO 1 (SENSOR_OBSTACLE)**

**Digital Sensor (IR, PIR, or Proximity):**
```
Sensor Module
┌────────────────────────┐
│  IR/PIR/Proximity      │
│                        │
│  VCC  OUT  GND         │
│  │    │    │           │
└──┼────┼────┼───────────┘
   │    │    │
   │    │    └──→ GND
   │    │
   │    └──────→ GPIO1 (Input)
   │
   └──────→ VCC (+5V)

State:
- No obstacle → GPIO reads HIGH (1)
- Obstacle detected → GPIO reads LOW (0)
```

**Alternative: Simple Digital Switch:**
```
VCC (+5V)
   │
   ├──[10kΩ]──┬─→ GPIO1 (Input)
   │          │
   │        Sensor/Switch
   │          │
   └──────────┴─→ GND
```

---

## 4️⃣  Relay/Buzzer Output (×1)

### **GPIO 22 (RELAY_POWER)**

**Power Control Relay with Transistor:**
```
GPIO22 ──[1kΩ]──┐
                 │
             Base of 2N2222 NPN Transistor
                 │
            ┌────┴────┐
            │          │
         Collector  Emitter
            │          │
            │          └──→ GND
            │
        Relay Coil (12V)
            │
        ┌───┴────┐
        │    ╱   │ 1N4007 Diode
     In │   │    │ (Protection)
  (from) ├──┤╱───┤
     12V │        │ Out
        │    ╲   │ (to machine)
        └────────┘
```

**Full Relay Circuit:**
```
            GPIO22 (Output)
                 │
                 ├──[1kΩ]──→ Base (B) of Transistor 2N2222
                 
            Collector (C)
                 │
            ┌────┴────┐
            │          │ 1N4007 Diode
            ├──╱───┤  (For voltage spike protection)
      12V  │    │ │
     (In)  elif     Relay Coil
            │    │ │
            ├──┐└───┤
            │  │
        Emitter (E)
            │
           GND

Relay Output:
        Terminal A ─→ Machine Power (+12V)
        Terminal B ─→ Output (switched)
        Terminal C ─→ GND
```

**Simplified Buzzer Connection (if using buzzer instead):**
```
GPIO22 ──[220Ω]──→ Buzzer+ ──→ +5V ──┐
                       Buzzer-        │
                           │          │
                           └─→ GND ←──┘
```

---

## 🔗 Complete RPI to Proteus Mapping

```
RPI GPIO Pin        →    Proteus Component      →    Connection
═══════════════════════════════════════════════════════════════════

OUTPUTS (GPIO High = Component ON):
──────────────────────────────────
GPIO 26 (Pin 37)   →    LED Red (220Ω)         →    LED26
GPIO 20 (Pin 38)   →    LED Yellow (220Ω)      →    LED20
GPIO 16 (Pin 36)   →    LED Green (220Ω)       →    LED16
GPIO 7 (Pin 26)    →    LED Yellow (220Ω)      →    LED7
GPIO 13 (Pin 33)   →    LED Green (220Ω)       →    LED13
GPIO 17 (Pin 11)   →    LED Blue (220Ω)        →    LED17

GPIO 22 (Pin 15)   →    Relay+2N2222+Diode     →    RELAY
                        (or Buzzer+220Ω)

INPUTS (GPIO Low = Button/Sensor Activated):
─────────────────────────────────────
GPIO 19 (Pin 35)   →    Push Button (10kΩ)    →    BTN_MATERIAL
GPIO 21 (Pin 40)   →    Push Button (10kΩ)    →    BTN_MAINT
GPIO 12 (Pin 32)   →    Push Button (10kΩ)    →    BTN_BREAK
GPIO 6 (Pin 31)    →    Push Button (10kΩ)    →    BTN_CANCEL
GPIO 27 (Pin 13)   →    Push Button (10kΩ)    →    BTN_RESET
GPIO 8 (Pin 24)    →    Push Button (10kΩ)    →    BTN_POWER

GPIO 1 (Pin ???)   →    IR/PIR Sensor (10kΩ)  →    SENSOR
                        Or Digital Switch
```

---

## 📐 Schematic Symbol Reference

```
LED Component:
    ────┐
        │ ├─→ Anode (+)
     │─ │      to VCC/Resistor
    ─┼─ │
        │ ├─→ Cathode (-)
    ────┘      to GND

Resistor (220Ω or 10kΩ):
    ┌────────┐
  ──┤        ├──
    └────────┘
    
Capacitor (if needed):
    ┌─┐
  ──┤ ├──
    ├─┤
    └─┘

Transistor 2N2222 (NPN):
      B (Base)
       │
      ╱
    ╱ C (Collector)
    │
    E (Emitter)

Diode 1N4007:
      │
    ┌─┘  (Cathode -)
    └─┐
      │  (Anode +)
      │

Button/Switch:
    ──┬┬──  (Closed = Connected)
      ││
      ├─  or  ───  (Open = Disconnected)
```

---

## ⚡ Power Distribution

```
Power Supply (+5V, GND)
        │
     ┌──┴──┐
   5V │     │ GND
      │     │
    ┌─┴──┬─┴──────────────────────────┐
    │    │                            │
   5V   GND                           │
    │    │                            │
    │    ├───→ All Pull-up 10kΩ (buttons)
    │    │
    │    ├───→ Button external circuits
    │    │
    │    ├───→ Sensor GND
    │    │
    │    ├───→ All LED Cathodes (-)
    │    │
    │    └───→ Transistor Emitter
    │
    ├───→ All Pull-up resistors (10kΩ) for buttons
    │
    ├───→ Sensor VCC
    │
    └───→ Relay Module VCC (12V if separate)
```

---

## 🔌 Proteus VSM Configuration

### **Virtual Firmware Platform Software** 
In Proteus (Tools → Firmware → Options):

```
1. Select Microcontroller: RPI3 or ATMEGA328
2. Set Clock Speed: 32 MHz (or default)
3. Enable I/O Pin Simulation
4. Point to Python script: main_proteus.py
5. Set Python path: C:\Python39\python.exe (or your version)
```

### **For Each GPIO Pin:**
```
Pin 26: Set as OUTPUT, name "GPIO26"
Pin 20: Set as OUTPUT, name "GPIO20"
...etc...
Pin 19: Set as INPUT PULLUP, name "GPIO19"
Pin 21: Set as INPUT PULLUP, name "GPIO21"
...etc...
Pin 1: Set as INPUT, name "GPIO1"
```

---

## ✅ Wiring Checklist

- [ ] All 6 LEDs connected to GPIO pins (26, 20, 16, 7, 13, 17)
  - [ ] Each with 220Ω resistor in series
  - [ ] Anode (long leg) to GPIO via resistor
  - [ ] Cathode (short leg) to GND

- [ ] All 6 Buttons connected to GPIO pins (19, 21, 12, 6, 27, 8)
  - [ ] Each with 10kΩ pull-up resistor to VCC
  - [ ] Button connects GPIO to GND when pressed

- [ ] Sensor connected to GPIO 1
  - [ ] VCC to power supply
  - [ ] GND to ground
  - [ ] Output to GPIO 1

- [ ] Relay/Buzzer connected to GPIO 22
  - [ ] Base resistor (1kΩ) from GPIO to transistor
  - [ ] Relay coil from collector to GND
  - [ ] Protection diode across relay coil
  - [ ] Relay output to machine

- [ ] Common GND rail (all negatives together)
- [ ] Common VCC rail (all positives together)
- [ ] All connections labeled with GPIO names

---

## 🚀 Testing After Wiring

In your Python code, test each pin:

```python
# Test LEDs
for pin in [26, 20, 16, 7, 13, 17]:
    set_led(pin, True)   # Turn ON
    time.sleep(0.5)
    set_led(pin, False)  # Turn OFF

# Test Buttons (check console for button press events)
# Test Sensor (press obstacle to simulate)
# Test Relay (should click when activated)
```

---

**Your circuit is now complete and ready for Proteus simulation!** ✅

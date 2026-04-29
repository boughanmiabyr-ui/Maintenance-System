#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple LCD Display Test for Proteus VSM
Tests if console output and LCD display are working
"""

import sys
import time

# Simple LCD Display Test
class LCD_I2C:
    """Virtual LCD display for testing"""
    
    def __init__(self, address=0x27, bus=1):
        self.address = address
        self.bus_num = bus
        self.line1 = ""
        self.line2 = ""
        print("[INIT] LCD initialized at I2C 0x{0:02x}".format(self.address))
        sys.stdout.flush()
    
    def display_text(self, line1, line2=""):
        """Display text on LCD"""
        line1 = str(line1)[:16].ljust(16)
        line2 = str(line2)[:16].ljust(16)
        
        if line1 == self.line1 and line2 == self.line2:
            return
        
        self.line1 = line1
        self.line2 = line2
        
        print("\n+---- LM016L LCD -+")
        print("|" + line1 + "|")
        print("|" + line2 + "|")
        print("+----------------+\n")
        sys.stdout.flush()

def main():
    """Test LCD display"""
    print("\n" + "="*50)
    print("LCD DISPLAY TEST")
    print("="*50)
    sys.stdout.flush()
    
    # Create LCD instance
    lcd = LCD_I2C(0x27, 1)
    time.sleep(1)
    
    # Test 1: Simple message
    print("[TEST 1] Displaying simple message...")
    sys.stdout.flush()
    lcd.display_text("Test 1", "Hello World")
    time.sleep(2)
    
    # Test 2: System ready
    print("[TEST 2] Displaying system ready...")
    sys.stdout.flush()
    lcd.display_text("System Ready", "4-Button Ready")
    time.sleep(2)
    
    # Test 3: Downtime alert
    print("[TEST 3] Displaying downtime alert...")
    sys.stdout.flush()
    lcd.display_text("DOWNTIME ALERT", "Press button...")
    time.sleep(2)
    
    # Test 4: Material change
    print("[TEST 4] Displaying material change...")
    sys.stdout.flush()
    lcd.display_text("Material Change", "180 sec timer")
    time.sleep(2)
    
    # Test 5: Break time
    print("[TEST 5] Displaying break time...")
    sys.stdout.flush()
    lcd.display_text("BREAK TIME", "Duration: 45s")
    time.sleep(2)
    
    # Test 6: Event cancelled
    print("[TEST 6] Displaying event cancelled...")
    sys.stdout.flush()
    lcd.display_text("EVENT CANCELLED", "DOWNTIME")
    time.sleep(2)
    
    print("\n" + "="*50)
    print("ALL TESTS COMPLETED!")
    print("If you see the LCD frames above, display is working!")
    print("="*50 + "\n")
    sys.stdout.flush()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("[ERROR] Test failed: {0}".format(str(e)))
        sys.stdout.flush()

# Also call main() at module level for Proteus VSM compatibility
main()

#!/usr/bin/env python3
"""
Test script for Sensor Count Display feature
Verifies that the API endpoint works correctly
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
SENSOR_API = f"{BASE_URL}/api/sensor/display-counts"

def test_sensor_display_api():
    """Test the sensor display API endpoint"""
    
    print("=" * 60)
    print("SENSOR COUNT DISPLAY API TEST")
    print("=" * 60)
    
    # Test with sample machine codes
    test_machines = [
        "MACHINE_001",
        "MACHINE_002", 
        "MACHINE_003"
    ]
    
    for machine_code in test_machines:
        print(f"\nTesting: {machine_code}")
        print("-" * 40)
        
        try:
            response = requests.get(f"{SENSOR_API}/{machine_code}", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Status: OK (200)")
                print(f"  Daily Count: {data.get('daily_count', 'N/A'):,}")
                print(f"  Total Count: {data.get('total_count', 'N/A'):,}")
                print(f"  Threshold: {data.get('threshold_value', 'N/A'):,}")
                print(f"  % to Threshold: {data.get('percentage_to_threshold', 'N/A')}%")
                print(f"  Maintenance Due: {data.get('threshold_reached', False)}")
                print(f"  Last Updated: {data.get('last_updated', 'N/A')}")
                
            elif response.status_code == 404:
                print(f"✗ Status: Not Found (404)")
                print(f"  Machine does not exist in system")
                
            else:
                print(f"✗ Status: Error ({response.status_code})")
                print(f"  Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"✗ Connection Error: Could not connect to {BASE_URL}")
            print(f"  Make sure the Flask app is running")
            
        except Exception as e:
            print(f"✗ Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

def test_html_page():
    """Test that the HTML page loads correctly"""
    
    print("\n" + "=" * 60)
    print("MACHINE STATUS PAGE TEST")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/machine-status", timeout=5)
        
        if response.status_code == 200:
            print(f"✓ Status: OK (200)")
            
            # Check for key elements
            checks = [
                ("sensor-count-card", "Sensor count card HTML"),
                ("threshold-bar", "Progress bar element"),
                ("daily-count", "Daily count display"),
                ("total-count", "Total count display"),
                ("updateSensorCounts", "JavaScript update function"),
                ("REFRESH_INTERVAL", "Auto-refresh interval config")
            ]
            
            for check_text, description in checks:
                if check_text in response.text:
                    print(f"  ✓ Found: {description}")
                else:
                    print(f"  ✗ Missing: {description}")
        else:
            print(f"✗ Status: Error ({response.status_code})")
            
    except requests.exceptions.ConnectionError:
        print(f"✗ Connection Error: Could not connect to {BASE_URL}")
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
    
    print("=" * 60)

if __name__ == "__main__":
    print(f"\nStarting tests at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target URL: {BASE_URL}\n")
    
    try:
        test_sensor_display_api()
        test_html_page()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    
    print(f"\nTests completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

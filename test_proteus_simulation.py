#!/usr/bin/env python3
"""
Test/Demo Script for Proteus Simulation
Run this to test the simulation without manual interaction
"""

import time
import requests
import json
from threading import Thread

# API Base URL
API_URL = "http://localhost:5001"

def test_results(name, passed):
    """Print test result"""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status}: {name}")

def wait_for_server(timeout=10):
    """Wait for Flask server to start"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{API_URL}/health", timeout=1)
            if response.status_code == 200:
                return True
        except:
            time.sleep(0.5)
    return False

def test_health_check():
    """Test health check endpoint"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        passed = response.status_code == 200
        test_results("Health Check", passed)
        if passed:
            print(f"  Response: {response.json()}")
        return passed
    except Exception as e:
        test_results("Health Check", False)
        print(f"  Error: {e}")
        return False

def test_get_status():
    """Test status endpoint"""
    try:
        response = requests.get(f"{API_URL}/status", timeout=5)
        passed = response.status_code == 200
        test_results("Get Status", passed)
        if passed:
            data = response.json()
            print(f"  Machine: {data.get('machine_name')}")
            print(f"  Status: {data.get('status')}")
            print(f"  Power: {'ON' if data.get('power_on') else 'OFF'}")
        return passed
    except Exception as e:
        test_results("Get Status", False)
        print(f"  Error: {e}")
        return False

def test_power_control():
    """Test power cut and restore"""
    try:
        # Cut power
        response = requests.post(
            f"{API_URL}/power_cut",
            json={"machine_name": "PROTEUS_SIM"},
            timeout=5
        )
        cut_passed = response.status_code == 200
        test_results("Power Cut", cut_passed)
        if cut_passed:
            print(f"  Response: {response.json()}")
        
        time.sleep(1)
        
        # Restore power
        response = requests.post(
            f"{API_URL}/power_restore",
            json={"machine_name": "PROTEUS_SIM"},
            timeout=5
        )
        restore_passed = response.status_code == 200
        test_results("Power Restore", restore_passed)
        if restore_passed:
            print(f"  Response: {response.json()}")
        
        return cut_passed and restore_passed
    except Exception as e:
        test_results("Power Control", False)
        print(f"  Error: {e}")
        return False

def test_wrong_machine_name():
    """Test error handling for wrong machine name"""
    try:
        response = requests.post(
            f"{API_URL}/power_cut",
            json={"machine_name": "WRONG_MACHINE"},
            timeout=5
        )
        passed = response.status_code == 400
        test_results("Wrong Machine Name (Error Handling)", passed)
        if passed:
            print(f"  Expected error: {response.json()}")
        return passed
    except Exception as e:
        test_results("Wrong Machine Name", False)
        print(f"  Error: {e}")
        return False

def test_send_event():
    """Test event endpoint"""
    try:
        response = requests.post(
            f"{API_URL}/event",
            json={
                "event_type": "downtime",
                "machine_name": "PROTEUS_SIM",
                "duration": 35.5
            },
            timeout=5
        )
        passed = response.status_code == 200
        test_results("Send Event", passed)
        if passed:
            print(f"  Response: {response.json()}")
        return passed
    except Exception as e:
        test_results("Send Event", False)
        print(f"  Error: {e}")
        return False

def test_reset_system():
    """Test system reset endpoint"""
    try:
        response = requests.post(
            f"{API_URL}/reset",
            json={"machine_name": "PROTEUS_SIM"},
            timeout=5
        )
        passed = response.status_code == 200
        test_results("System Reset", passed)
        if passed:
            print(f"  Response: {response.json()}")
        return passed
    except Exception as e:
        test_results("System Reset", False)
        print(f"  Error: {e}")
        return False

def test_api_docs():
    """Test API documentation endpoint"""
    try:
        response = requests.get(f"{API_URL}/api/docs", timeout=5)
        passed = response.status_code == 200
        test_results("API Documentation", passed)
        if passed:
            docs = response.json()
            print(f"  Available endpoints: {len(docs.get('endpoints', {}))}")
        return passed
    except Exception as e:
        test_results("API Docs", False)
        print(f"  Error: {e}")
        return False

def test_invalid_endpoint():
    """Test 404 error handling"""
    try:
        response = requests.get(f"{API_URL}/invalid/endpoint", timeout=5)
        passed = response.status_code == 404
        test_results("Invalid Endpoint (404)", passed)
        if passed:
            print(f"  Response: {response.json()}")
        return passed
    except Exception as e:
        test_results("Invalid Endpoint", False)
        print(f"  Error: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("PROTEUS SIMULATION - API TESTS")
    print("="*60 + "\n")
    
    print("[1/2] Waiting for Flask server to start...")
    if not wait_for_server():
        print("ERROR: Flask server not responding after 10 seconds")
        print("Make sure to run 'python proteus_main.py' first!")
        return
    print("✓ Server is ready\n")
    
    print("[2/2] Running tests...\n")
    
    results = []
    
    # Basic tests
    print("--- Basic Functionality ---")
    results.append(test_health_check())
    results.append(test_get_status())
    print()
    
    # Power control tests
    print("--- Power Control ---")
    results.append(test_power_control())
    print()
    
    # Event tests
    print("--- Event Handling ---")
    results.append(test_send_event())
    results.append(test_reset_system())
    print()
    
    # Documentation tests
    print("--- API Documentation ---")
    results.append(test_api_docs())
    print()
    
    # Error handling tests
    print("--- Error Handling ---")
    results.append(test_wrong_machine_name())
    results.append(test_invalid_endpoint())
    print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    print("="*60)
    print(f"TEST SUMMARY: {passed}/{total} passed")
    print("="*60 + "\n")
    
    if passed == total:
        print("✓ All tests passed! Simulation is working correctly.")
    else:
        print(f"✗ {total - passed} test(s) failed. Check the output above.")

if __name__ == "__main__":
    run_all_tests()

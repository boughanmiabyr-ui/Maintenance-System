#!/usr/bin/env python
"""Comprehensive app functionality test"""
import os
from dotenv import load_dotenv

load_dotenv()

try:
    print("=" * 60)
    print("COMPREHENSIVE APP FUNCTIONALITY TEST")
    print("=" * 60)
    
    from app import create_app, db
    from app.models import Machine, Material, User, MaintenanceSchedule
    
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    
    with app.app_context():
        tests_passed = 0
        tests_total = 0
        
        # Test 1: Machine queries
        tests_total += 1
        print("\n[1/5] Testing Machine queries...")
        try:
            total = Machine.query.filter_by(status='active').count()
            machines = Machine.query.filter_by(status='active').all()
            print(f"  SUCCESS: {total} active machines")
            tests_passed += 1
        except Exception as e:
            print(f"  FAILED: {e}")
        
        # Test 2: Material queries
        tests_total += 1
        print("\n[2/5] Testing Material queries...")
        try:
            materials = Material.query.limit(5).all()
            print(f"  SUCCESS: Retrieved {len(materials)} materials")
            tests_passed += 1
        except Exception as e:
            print(f"  FAILED: {e}")
        
        # Test 3: User queries
        tests_total += 1
        print("\n[3/5] Testing User queries...")
        try:
            users = User.query.filter(User.role.in_(['admin', 'supervisor'])).all()
            print(f"  SUCCESS: Retrieved {len(users)} admin/supervisor users")
            tests_passed += 1
        except Exception as e:
            print(f"  FAILED: {e}")
        
        # Test 4: MaintenanceSchedule queries
        tests_total += 1
        print("\n[4/5] Testing MaintenanceSchedule queries...")
        try:
            schedules = MaintenanceSchedule.query.limit(5).all()
            print(f"  SUCCESS: Retrieved {len(schedules)} schedules")
            tests_passed += 1
        except Exception as e:
            print(f"  FAILED: {e}")
        
        # Test 5: Complex dashboard query
        tests_total += 1
        print("\n[5/5] Testing complex dashboard queries...")
        try:
            active_machines = Machine.query.filter_by(status='active').count()
            pending_schedules = MaintenanceSchedule.query.filter(
                MaintenanceSchedule.status.in_(['scheduled', 'overdue'])
            ).count()
            print(f"  SUCCESS: Active machines={active_machines}, Pending schedules={pending_schedules}")
            tests_passed += 1
        except Exception as e:
            print(f"  FAILED: {e}")
        
        print("\n" + "=" * 60)
        print(f"RESULTS: {tests_passed}/{tests_total} tests passed")
        print("=" * 60)
        
        if tests_passed == tests_total:
            print("\nSTATUS: ALL TESTS PASSED - APP IS READY!")
        else:
            print(f"\nSTATUS: {tests_total - tests_passed} test(s) failed")
        
except Exception as e:
    print(f"\nFATAL ERROR: {e}")
    import traceback
    traceback.print_exc()

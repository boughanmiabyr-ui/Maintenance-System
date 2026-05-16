#!/usr/bin/env python
"""Final comprehensive fix verification"""
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 80)
print("FINAL COMPREHENSIVE FIX VERIFICATION".center(80))
print("=" * 80)

tests_results = []

# Test 1: Database connection
print("\n[1/6] Database Connection...")
try:
    import pymysql
    db_user = os.getenv('MYSQL_USER', 'root')
    db_password = os.getenv('MYSQL_PASSWORD', 'Passw0rd123')
    db_host = os.getenv('MYSQL_HOST', 'localhost')
    db_name = os.getenv('MYSQL_DB', 'maintenance_system_v2')
    
    conn = pymysql.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM machines")
    conn.close()
    print("  PASSED: Database connected")
    tests_results.append(True)
except Exception as e:
    print(f"  FAILED: {e}")
    tests_results.append(False)

# Test 2: Material type column
print("\n[2/6] Material Type Column...")
try:
    from app import create_app, db
    from app.models import Material
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    with app.app_context():
        materials = Material.query.limit(1).all()
        material_types = [m.material_type for m in materials]
    print("  PASSED: material_type column accessible")
    tests_results.append(True)
except Exception as e:
    print(f"  FAILED: {e}")
    tests_results.append(False)

# Test 3: Machine operation_count column
print("\n[3/6] Machine Operation Count Column...")
try:
    from app import create_app, db
    from app.models import Machine
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    with app.app_context():
        machines = Machine.query.limit(1).all()
        op_counts = [m.operation_count for m in machines]
    print("  PASSED: operation_count column accessible")
    tests_results.append(True)
except Exception as e:
    print(f"  FAILED: {e}")
    tests_results.append(False)

# Test 4: Dashboard query
print("\n[4/6] Dashboard Active Machines Query...")
try:
    from app import create_app, db
    from app.models import Machine
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    with app.app_context():
        total = Machine.query.filter_by(status='active').count()
    print(f"  PASSED: Found {total} active machines")
    tests_results.append(True)
except Exception as e:
    print(f"  FAILED: {e}")
    tests_results.append(False)

# Test 5: Flask app initialization
print("\n[5/6] Flask App Initialization...")
try:
    from app import create_app
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    routes_count = len(list(app.url_map.iter_rules()))
    print(f"  PASSED: {routes_count} routes registered")
    tests_results.append(True)
except Exception as e:
    print(f"  FAILED: {e}")
    tests_results.append(False)

# Test 6: Flask client test
print("\n[6/6] Flask Client Test...")
try:
    from app import create_app
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    client = app.test_client()
    response = client.get('/')
    if response.status_code in [200, 302]:
        print(f"  PASSED: Index route responds with {response.status_code}")
        tests_results.append(True)
    else:
        print(f"  FAILED: Unexpected status {response.status_code}")
        tests_results.append(False)
except Exception as e:
    print(f"  FAILED: {e}")
    tests_results.append(False)

# Summary
print("\n" + "=" * 80)
passed = sum(tests_results)
total = len(tests_results)
print(f"RESULTS: {passed}/{total} tests passed".center(80))

if passed == total:
    print("\n" + "STATUS: ALL SYSTEMS OPERATIONAL - APP IS READY TO USE!".center(80))
else:
    print(f"\n" + f"STATUS: {total - passed} issue(s) remain".center(80))

print("=" * 80)

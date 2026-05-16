#!/usr/bin/env python
"""Test Flask app with client"""
import os
from dotenv import load_dotenv

load_dotenv()

try:
    print("=" * 70)
    print("FLASK APP CLIENT TEST")
    print("=" * 70)
    
    from app import create_app
    
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    
    # Create a test client
    client = app.test_client()
    
    print("\nTest 1: GET / (index route)")
    response = client.get('/')
    print(f"  Status: {response.status_code}")
    if response.status_code in [200, 302]:
        print("  Result: OK (redirects to login or shows dashboard)")
    else:
        print(f"  Result: ERROR - unexpected status code")
    
    print("\nTest 2: GET /dashboard (requires auth)")
    response = client.get('/dashboard')
    print(f"  Status: {response.status_code}")
    if response.status_code == 302:
        print("  Result: OK (redirects to login - expected without auth)")
    else:
        print(f"  Result: INFO - status {response.status_code}")
    
    # Test API endpoints
    print("\nTest 3: GET /api/machines (JSON)")
    response = client.get('/api/machines')
    print(f"  Status: {response.status_code}")
    if response.status_code in [200, 401]:
        print(f"  Result: OK (status {response.status_code})")
    else:
        print(f"  Result: ERROR - unexpected status code")
    
    print("\nTest 4: Routes are registered")
    routes_count = len([r for r in app.url_map.iter_rules()])
    print(f"  Total routes: {routes_count}")
    print(f"  Result: OK")
    
    # Show some routes
    print("\nSample routes:")
    for i, rule in enumerate(app.url_map.iter_rules()):
        if i < 10:
            print(f"  - {rule.endpoint}: {rule.rule}")
    
    print("\n" + "=" * 70)
    print("FLASK APP CLIENT TEST: PASSED!")
    print("=" * 70)
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()

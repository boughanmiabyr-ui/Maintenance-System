#!/usr/bin/env python
"""Test dashboard route"""
import os
from dotenv import load_dotenv

load_dotenv()

try:
    print("Testing dashboard route...")
    
    from app import create_app
    from app.models import Machine
    
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    
    with app.app_context():
        # Test the exact query from dashboard
        print("\nTest: Machine.query.filter_by(status='active').count()")
        total_machines = Machine.query.filter_by(status='active').count()
        print(f"SUCCESS: Found {total_machines} active machines")
        
        # Try with .all() and then count
        print("\nTest: Machine.query.filter_by(status='active').all()")
        machines = Machine.query.filter_by(status='active').all()
        print(f"SUCCESS: Retrieved {len(machines)} active machines")
        
        print("\nDashboard query tests PASSED!")
        
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()

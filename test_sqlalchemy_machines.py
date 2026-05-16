#!/usr/bin/env python
"""Test SQLAlchemy Machine query"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

try:
    print("Initializing Flask app...")
    from app import create_app, db
    
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    
    with app.app_context():
        print("Testing SQLAlchemy Machine queries...")
        
        # Import models
        from app.models import Machine
        
        # Try the failing query - count active machines
        print("\nTest 1: Count active machines...")
        active_count = db.session.query(Machine).filter_by(status='active').count()
        print(f"SUCCESS: Found {active_count} active machines")
        
        # Try querying with all columns
        print("\nTest 2: Query active machines with all columns...")
        machines = db.session.query(Machine).filter_by(status='active').limit(5).all()
        print(f"SUCCESS: Retrieved {len(machines)} machines")
        
        if machines:
            m = machines[0]
            print(f"\nSample machine:")
            print(f"  Code: {m.machine_code}")
            print(f"  Name: {m.machine_name}")
            print(f"  Operation Count: {m.operation_count}")
            print(f"  Threshold: {m.conditional_maintenance_threshold}")
            print(f"  Status: {m.status}")
        
        # Try the complex count subquery that was failing
        print("\nTest 3: Complex count subquery (the failing query)...")
        from sqlalchemy import func
        
        subquery = db.session.query(Machine).filter_by(status='active')
        count = db.session.query(func.count()).select_entity_from(subquery).scalar()
        print(f"SUCCESS: Subquery count = {count}")
        
        print("\nAll SQLAlchemy Machine queries PASSED!")
        
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

#!/usr/bin/env python
"""Test app database access"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

try:
    print("Initializing Flask app...")
    from app import create_app, db
    
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    
    with app.app_context():
        print("Testing database query...")
        
        # Import models
        from app.models import Material
        
        # Try to query materials
        materials = Material.query.limit(5).all()
        
        print(f"SUCCESS: Queried {len(materials)} materials")
        
        if materials:
            print(f"\nFirst material: {materials[0].code} - {materials[0].name}")
            print(f"  - Material type: {materials[0].material_type}")
            print(f"  - Category: {materials[0].category}")
        
        print("\nDatabase access test PASSED!")
        
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

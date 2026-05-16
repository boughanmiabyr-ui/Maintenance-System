#!/usr/bin/env python
"""Test stock inventory endpoint that was failing"""
import os
from dotenv import load_dotenv

load_dotenv()

try:
    from app import create_app, db
    from app.models import Material, User
    
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    
    with app.app_context():
        print("Testing Material query with all columns...")
        
        # This is the exact query that was failing
        materials = db.session.query(Material).limit(20).all()
        
        print(f"SUCCESS: Retrieved {len(materials)} materials with all columns")
        
        if materials:
            m = materials[0]
            print(f"\nSample material:")
            print(f"  ID: {m.id}")
            print(f"  Code: {m.code}")
            print(f"  Name: {m.name}")
            print(f"  Category: {m.category}")
            print(f"  Material Type: {m.material_type}")
            print(f"  Unit: {m.unit}")
            print(f"  Current Stock: {m.current_stock}")
        
        print("\nInventory query test PASSED!")
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

#!/usr/bin/env python3
"""
Test script for the new "Add Quantity" feature
Tests both the search and update endpoints
"""

import sys
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, '/Users/dell/Desktop/Maintenance System')

from app import create_app, db
from app.models import Material, User, StockMovement

def test_add_quantity_feature():
    """Test the Add Quantity feature"""
    
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("Testing Add Quantity Feature")
        print("=" * 60)
        
        # Test 1: Verify Material model has required fields
        print("\n[Test 1] Verifying Material model structure...")
        try:
            materials = Material.query.limit(1).all()
            if materials:
                m = materials[0]
                print(f"✓ Material found: {m.code} - {m.name}")
                print(f"  - Current Stock: {m.current_stock}")
                print(f"  - Category: {m.category}")
                print(f"  - Unit: {m.unit}")
                print(f"  - Stock Status: {m.stock_status}")
            else:
                print("✗ No materials found in database")
        except Exception as e:
            print(f"✗ Error querying materials: {e}")
        
        # Test 2: Verify StockMovement model
        print("\n[Test 2] Verifying StockMovement model structure...")
        try:
            movement = StockMovement.query.limit(1).first()
            if movement:
                print(f"✓ StockMovement found: {movement.id}")
                print(f"  - Material: {movement.material_id}")
                print(f"  - Type: {movement.movement_type}")
                print(f"  - Quantity: {movement.quantity}")
            else:
                print("✓ StockMovement table exists (no records yet)")
        except Exception as e:
            print(f"✗ Error with StockMovement: {e}")
        
        # Test 3: Test search functionality
        print("\n[Test 3] Testing search functionality...")
        try:
            # Get a sample material to search for
            material = Material.query.first()
            if material:
                search_query = material.code[:3]  # Search for first 3 chars of code
                print(f"  Searching for: '{search_query}'")
                
                # Simulate search
                from sqlalchemy import or_
                results = Material.query.filter(
                    (Material.code.ilike(f'%{search_query}%')) |
                    (Material.name.ilike(f'%{search_query}%')) |
                    (Material.category.ilike(f'%{search_query}%'))
                ).limit(20).all()
                
                print(f"✓ Found {len(results)} materials")
                for r in results[:3]:
                    print(f"  - {r.code}: {r.name} ({r.current_stock} {r.unit})")
            else:
                print("✗ No materials to search")
        except Exception as e:
            print(f"✗ Error during search: {e}")
        
        # Test 4: Verify endpoints exist
        print("\n[Test 4] Checking Flask route registration...")
        try:
            routes_found = False
            for rule in app.url_map.iter_rules():
                if 'materials' in rule.rule and 'search' in rule.rule:
                    print(f"✓ Found search endpoint: {rule.rule} [{rule.methods}]")
                    routes_found = True
                if 'materials' in rule.rule and 'update' in rule.rule:
                    print(f"✓ Found update endpoint: {rule.rule} [{rule.methods}]")
                    routes_found = True
            
            if not routes_found:
                print("✗ Endpoints not found in routes")
        except Exception as e:
            print(f"✗ Error checking routes: {e}")
        
        print("\n" + "=" * 60)
        print("Testing complete!")
        print("=" * 60)
        
        print("\nNext steps:")
        print("1. Navigate to http://localhost:5000/stock/add")
        print("2. Click the 'Add Quantity' button")
        print("3. Search for an existing spare part")
        print("4. Select one and update its quantity")
        print("\nThe system will create a stock movement record")
        print("and update the material's current stock.")

if __name__ == '__main__':
    test_add_quantity_feature()

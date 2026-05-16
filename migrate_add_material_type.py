#!/usr/bin/env python
"""
Database Migration Script
Adds material_type column to materials table and auto-categorizes materials

Usage:
    python migrate_add_material_type.py
"""

import os
import sys
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def migrate():
    """Add material_type column to materials table and categorize materials"""
    try:
        from app import create_app, db
        
        # Create Flask app with minimal initialization
        app = create_app(os.getenv('FLASK_ENV', 'development'))
        
        with app.app_context():
            # Wait a moment to let background threads settle
            time.sleep(1)
            
            # Get the database connection
            connection = db.engine.raw_connection()
            cursor = connection.cursor()
            
            print("Starting database migration for material_type...")
            
            # Check if material_type column exists
            cursor.execute("""
                SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME='materials' AND COLUMN_NAME='material_type'
            """)
            material_type_exists = cursor.fetchone() is not None
            
            # Add material_type column if it doesn't exist
            if not material_type_exists:
                print("Adding material_type column to materials table...")
                try:
                    cursor.execute("""
                        ALTER TABLE materials
                        ADD COLUMN material_type VARCHAR(50) DEFAULT 'standard',
                        ADD INDEX ix_materials_material_type (material_type)
                    """)
                    connection.commit()
                    print("✓ material_type column added")
                    
                    # Auto-categorize materials based on category
                    print("Auto-categorizing materials based on their category...")
                    
                    specific_categories = [
                        'Engine Parts', 'Hydraulic Components', 'Bearings', 'Seals',
                        'Belts & Chains', 'Motors', 'Sensors', 'Control Units',
                        'Valves', 'Pumps', 'Compressors', 'Drive Components',
                        'Mechanical Parts', 'Electrical Components', 'Pneumatic Components',
                        'Transmission', 'Gearbox', 'Coupling', 'Clutch', 'Brake',
                        'Filter', 'Heat Exchanger', 'Reservoir', 'Actuators'
                    ]
                    
                    specific_placeholders = ','.join(['%s'] * len(specific_categories))
                    
                    # Update specific materials
                    cursor.execute(f"""
                        UPDATE materials 
                        SET material_type = 'specific'
                        WHERE category IN ({specific_placeholders})
                    """, specific_categories)
                    connection.commit()
                    
                    # Verify changes
                    cursor.execute("SELECT COUNT(*) FROM materials WHERE material_type = 'specific'")
                    specific_count = cursor.fetchone()[0]
                    cursor.execute("SELECT COUNT(*) FROM materials WHERE material_type = 'standard'")
                    standard_count = cursor.fetchone()[0]
                    
                    print(f"✓ Categorized {specific_count} materials as 'specific'")
                    print(f"✓ Categorized {standard_count} materials as 'standard'")
                    
                except Exception as e:
                    if "Duplicate column" in str(e) or "already exists" in str(e).lower():
                        print("✓ material_type column already exists")
                    else:
                        raise
                
            else:
                print("✓ material_type column already exists")
            
            cursor.close()
            connection.close()
            
            print("\n✓ Migration completed successfully!")
            return True
            
    except Exception as e:
        print(f"\n✗ Migration failed with error:")
        print(f"  {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = migrate()
    sys.exit(0 if success else 1)

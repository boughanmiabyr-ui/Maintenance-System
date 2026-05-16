#!/usr/bin/env python
"""
Database Migration Script
Adds zone_id and machine_id columns to materials table

Usage:
    python migrate_materials_zone_machine.py
"""

import os
import sys
from dotenv import load_dotenv
from app import create_app, db

# Load environment variables
load_dotenv()

# Create Flask app
app = create_app(os.getenv('FLASK_ENV', 'development'))

def migrate():
    """Add zone_id and machine_id columns to materials table"""
    with app.app_context():
        try:
            # Get the database connection
            connection = db.engine.raw_connection()
            cursor = connection.cursor()
            
            print("Starting database migration for materials table...")
            
            # Check if zone_id column exists
            cursor.execute("""
                SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME='materials' AND COLUMN_NAME='zone_id'
            """)
            zone_id_exists = cursor.fetchone() is not None
            
            # Check if machine_id column exists
            cursor.execute("""
                SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME='materials' AND COLUMN_NAME='machine_id'
            """)
            machine_id_exists = cursor.fetchone() is not None
            
            # Add zone_id column if it doesn't exist
            if not zone_id_exists:
                print("Adding zone_id column to materials table...")
                cursor.execute("""
                    ALTER TABLE materials
                    ADD COLUMN zone_id INT NULL,
                    ADD FOREIGN KEY (zone_id) REFERENCES zones(id)
                """)
                print("[OK] zone_id column added successfully")
            else:
                print("[OK] zone_id column already exists")
            
            # Add machine_id column if it doesn't exist
            if not machine_id_exists:
                print("Adding machine_id column to materials table...")
                cursor.execute("""
                    ALTER TABLE materials
                    ADD COLUMN machine_id INT NULL,
                    ADD FOREIGN KEY (machine_id) REFERENCES machines(id)
                """)
                print("[OK] machine_id column added successfully")
            else:
                print("[OK] machine_id column already exists")
            
            connection.commit()
            cursor.close()
            connection.close()
            
            print("\n[OK] Database migration completed successfully!")
            return True
            
        except Exception as e:
            print(f"\n[ERROR] Migration failed: {str(e)}")
            if connection:
                connection.rollback()
                cursor.close()
                connection.close()
            return False

if __name__ == '__main__':
    success = migrate()
    sys.exit(0 if success else 1)

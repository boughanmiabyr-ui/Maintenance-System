#!/usr/bin/env python
"""
Database Migration Script
Adds zone_id and machine_id columns to spare_parts_demands table

Usage:
    python migrate_add_zone_machine_columns.py
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
    """Add missing columns to spare_parts_demands table"""
    with app.app_context():
        try:
            # Get the database connection
            connection = db.engine.raw_connection()
            cursor = connection.cursor()
            
            print("Starting database migration...")
            
            # Check if zone_id column exists
            cursor.execute("""
                SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME='spare_parts_demands' AND COLUMN_NAME='zone_id'
            """)
            zone_id_exists = cursor.fetchone() is not None
            
            # Check if machine_id column exists
            cursor.execute("""
                SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME='spare_parts_demands' AND COLUMN_NAME='machine_id'
            """)
            machine_id_exists = cursor.fetchone() is not None
            
            # Add zone_id column if it doesn't exist
            if not zone_id_exists:
                print("Adding zone_id column to spare_parts_demands table...")
                cursor.execute("""
                    ALTER TABLE spare_parts_demands
                    ADD COLUMN zone_id INT NULL
                """)
                print("✓ zone_id column added")
            else:
                print("✓ zone_id column already exists")
            
            # Add machine_id column if it doesn't exist
            if not machine_id_exists:
                print("Adding machine_id column to spare_parts_demands table...")
                cursor.execute("""
                    ALTER TABLE spare_parts_demands
                    ADD COLUMN machine_id INT NULL
                """)
                print("✓ machine_id column added")
            else:
                print("✓ machine_id column already exists")
            
            # Add indexes if columns were added
            if not zone_id_exists:
                try:
                    cursor.execute("""
                        ALTER TABLE spare_parts_demands
                        ADD INDEX ix_spare_parts_demands_zone_id (zone_id)
                    """)
                    print("✓ zone_id index added")
                except:
                    pass  # Index might already exist
            
            if not machine_id_exists:
                try:
                    cursor.execute("""
                        ALTER TABLE spare_parts_demands
                        ADD INDEX ix_spare_parts_demands_machine_id (machine_id)
                    """)
                    print("✓ machine_id index added")
                except:
                    pass  # Index might already exist
            
            # Add foreign key constraints if they don't exist
            cursor.execute("""
                SELECT CONSTRAINT_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                WHERE TABLE_NAME='spare_parts_demands' AND COLUMN_NAME='zone_id' 
                AND REFERENCED_TABLE_NAME='zones'
            """)
            zone_fk_exists = cursor.fetchone() is not None
            
            cursor.execute("""
                SELECT CONSTRAINT_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                WHERE TABLE_NAME='spare_parts_demands' AND COLUMN_NAME='machine_id' 
                AND REFERENCED_TABLE_NAME='machines'
            """)
            machine_fk_exists = cursor.fetchone() is not None
            
            if not zone_fk_exists and zone_id_exists:
                try:
                    cursor.execute("""
                        ALTER TABLE spare_parts_demands
                        ADD CONSTRAINT fk_spare_parts_demands_zone_id 
                        FOREIGN KEY (zone_id) REFERENCES zones(id)
                    """)
                    print("✓ zone_id foreign key constraint added")
                except Exception as e:
                    if "already exists" in str(e).lower():
                        print("✓ zone_id foreign key constraint already exists")
                    else:
                        print(f"⚠ Could not add zone_id foreign key: {str(e)}")
            
            if not machine_fk_exists and machine_id_exists:
                try:
                    cursor.execute("""
                        ALTER TABLE spare_parts_demands
                        ADD CONSTRAINT fk_spare_parts_demands_machine_id 
                        FOREIGN KEY (machine_id) REFERENCES machines(id)
                    """)
                    print("✓ machine_id foreign key constraint added")
                except Exception as e:
                    if "already exists" in str(e).lower():
                        print("✓ machine_id foreign key constraint already exists")
                    else:
                        print(f"⚠ Could not add machine_id foreign key: {str(e)}")
            
            connection.commit()
            cursor.close()
            connection.close()
            
            print("\n✓ Migration completed successfully!")
            print("\nNote: zone_id and machine_id are currently nullable.")
            print("New demand records will be required to specify zone and machine.")
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

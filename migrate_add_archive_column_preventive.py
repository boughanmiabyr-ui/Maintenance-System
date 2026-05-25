#!/usr/bin/env python3
"""
Migration Script: Add archive_date column to preventive_maintenance_executions table
Purpose: Sync database schema with SQLAlchemy model
Date: 2026-05-21
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
import pymysql

def migrate():
    """Add archive_date column to preventive_maintenance_executions table"""
    
    # Get database connection details from config
    connection_config = {
        'host': Config.MYSQL_HOST,
        'user': Config.MYSQL_USER,
        'password': Config.MYSQL_PASSWORD,
        'database': Config.MYSQL_DB,
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor
    }
    
    try:
        # Connect to database
        connection = pymysql.connect(**connection_config)
        cursor = connection.cursor()
        
        print(f"✓ Connected to database: {Config.MYSQL_DB}")
        
        # Step 1: Check if column already exists
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME='preventive_maintenance_executions' 
            AND COLUMN_NAME='archive_date' 
            AND TABLE_SCHEMA=%s
        """, (Config.MYSQL_DB,))
        
        if cursor.fetchone():
            print("✓ Column 'archive_date' already exists in preventive_maintenance_executions")
            return True
        
        # Step 2: Add archive_date column
        print("\nAdding 'archive_date' column to preventive_maintenance_executions...")
        cursor.execute("""
            ALTER TABLE preventive_maintenance_executions 
            ADD COLUMN archive_date DATETIME NULL AFTER updated_at
        """)
        print("✓ Column 'archive_date' added successfully")
        
        # Step 3: Create index for archive_date
        print("\nCreating index on archive_date...")
        cursor.execute("""
            ALTER TABLE preventive_maintenance_executions 
            ADD INDEX idx_archive_date (archive_date)
        """)
        print("✓ Index 'idx_archive_date' created successfully")
        
        # Step 4: Create composite index for status and archive_date
        print("\nCreating composite index on status and archive_date...")
        cursor.execute("""
            ALTER TABLE preventive_maintenance_executions 
            ADD INDEX idx_status_archive (status, archive_date)
        """)
        print("✓ Index 'idx_status_archive' created successfully")
        
        # Step 5: Verify the changes
        print("\n✓ Verifying table structure...")
        cursor.execute("""
            DESCRIBE preventive_maintenance_executions
        """)
        columns = cursor.fetchall()
        
        # Print relevant columns
        print("\nRelevant columns in preventive_maintenance_executions:")
        for col in columns:
            if col['Field'] in ['updated_at', 'archive_date']:
                print(f"  - {col['Field']}: {col['Type']} {'NULL' if col['Null'] == 'YES' else 'NOT NULL'}")
        
        connection.commit()
        print("\n✅ Migration completed successfully!")
        return True
        
    except pymysql.Error as e:
        print(f"❌ Database error: {e}")
        connection.rollback()
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

if __name__ == '__main__':
    success = migrate()
    sys.exit(0 if success else 1)

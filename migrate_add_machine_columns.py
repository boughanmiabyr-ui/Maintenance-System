#!/usr/bin/env python
"""
Database Migration Script
Adds missing columns to machines table for conditional maintenance

Usage:
    python migrate_add_machine_columns.py
"""

import os
import sys
import time
from dotenv import load_dotenv

load_dotenv()

def migrate():
    """Add missing columns to machines table"""
    try:
        import pymysql
        from pymysql import cursors
        
        # Database config
        db_user = os.getenv('MYSQL_USER', 'root')
        db_password = os.getenv('MYSQL_PASSWORD', 'Passw0rd123')
        db_host = os.getenv('MYSQL_HOST', 'localhost')
        db_name = os.getenv('MYSQL_DB', 'maintenance_system_v2')
        
        connection = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name,
            charset='utf8mb4',
            cursorclass=cursors.DictCursor
        )
        
        cursor = connection.cursor()
        
        print("Starting database migration for machines table...")
        
        # Get current columns
        cursor.execute("""
            SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME='machines' AND TABLE_SCHEMA=%s
        """, [db_name])
        
        current_columns = [row['COLUMN_NAME'] for row in cursor.fetchall()]
        print(f"\nCurrent machines columns: {len(current_columns)}")
        
        # Columns to add
        columns_to_add = {
            'operation_count': 'INT DEFAULT 0',
            'conditional_maintenance_threshold': 'INT DEFAULT 300000',
            'last_conditional_reset_date': 'DATETIME NULL',
            'last_conditional_replacement_date': 'DATETIME NULL'
        }
        
        # Check and add missing columns
        added_count = 0
        for col_name, col_type in columns_to_add.items():
            if col_name not in current_columns:
                print(f"\nAdding column: {col_name}...")
                try:
                    if col_name == 'operation_count':
                        cursor.execute(f"""
                            ALTER TABLE machines
                            ADD COLUMN {col_name} {col_type},
                            ADD INDEX ix_machines_{col_name} ({col_name})
                        """)
                    else:
                        cursor.execute(f"""
                            ALTER TABLE machines
                            ADD COLUMN {col_name} {col_type}
                        """)
                    print(f"  ✓ Added {col_name}")
                    added_count += 1
                except Exception as e:
                    print(f"  ! Could not add {col_name}: {e}")
            else:
                print(f"  ✓ {col_name} already exists")
        
        connection.commit()
        
        # Verify
        cursor.execute("""
            SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME='machines' AND TABLE_SCHEMA=%s
        """, [db_name])
        
        final_columns = [row['COLUMN_NAME'] for row in cursor.fetchall()]
        print(f"\nFinal machines columns: {len(final_columns)}")
        print(f"Columns added: {added_count}")
        
        cursor.close()
        connection.close()
        
        print("\n✓ Migration completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Error during migration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    migrate()

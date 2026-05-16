#!/usr/bin/env python
"""
Direct SQL Migration Script
Adds zone_id and machine_id columns to materials table
"""

import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DB_HOST = os.getenv('MYSQL_HOST', 'localhost')
DB_USER = os.getenv('MYSQL_USER', 'root')
DB_PASSWORD = os.getenv('MYSQL_PASSWORD', 'Passw0rd123')
DB_NAME = os.getenv('MYSQL_DB', 'maintenance_system_v2')

def migrate_directly():
    """Add columns directly via SQL"""
    try:
        # Connect to database
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        cursor = conn.cursor()
        print("Connected to database:", DB_NAME)
        
        # Check existing columns
        cursor.execute("""
            SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA=%s AND TABLE_NAME='materials'
        """, (DB_NAME,))
        
        existing_columns = [row['COLUMN_NAME'] for row in cursor.fetchall()]
        print("\nExisting columns in materials table:")
        print(existing_columns)
        
        # Add zone_id if missing
        if 'zone_id' not in existing_columns:
            print("\nAdding zone_id column...")
            try:
                cursor.execute("ALTER TABLE materials ADD COLUMN zone_id INT NULL")
                print("[OK] zone_id column added")
            except Exception as e:
                print(f"[WARNING] Error adding zone_id: {e}")
        else:
            print("\n[OK] zone_id column already exists")
        
        # Add machine_id if missing  
        if 'machine_id' not in existing_columns:
            print("\nAdding machine_id column...")
            try:
                cursor.execute("ALTER TABLE materials ADD COLUMN machine_id INT NULL")
                print("[OK] machine_id column added")
            except Exception as e:
                print(f"[WARNING] Error adding machine_id: {e}")
        else:
            print("\n[OK] machine_id column already exists")
        
        # Add lifespan_days if missing
        if 'lifespan_days' not in existing_columns:
            print("\nAdding lifespan_days column...")
            try:
                cursor.execute("ALTER TABLE materials ADD COLUMN lifespan_days INT NULL")
                print("[OK] lifespan_days column added")
            except Exception as e:
                print(f"[WARNING] Error adding lifespan_days: {e}")
        else:
            print("[OK] lifespan_days column already exists")
        
        # Add stock_entry_date if missing
        if 'stock_entry_date' not in existing_columns:
            print("\nAdding stock_entry_date column...")
            try:
                cursor.execute("ALTER TABLE materials ADD COLUMN stock_entry_date DATETIME NULL")
                print("[OK] stock_entry_date column added")
            except Exception as e:
                print(f"[WARNING] Error adding stock_entry_date: {e}")
        else:
            print("[OK] stock_entry_date column already exists")
        
        # Add stock_registration_date if missing
        if 'stock_registration_date' not in existing_columns:
            print("\nAdding stock_registration_date column...")
            try:
                cursor.execute("ALTER TABLE materials ADD COLUMN stock_registration_date DATETIME DEFAULT CURRENT_TIMESTAMP")
                print("[OK] stock_registration_date column added")
            except Exception as e:
                print(f"[WARNING] Error adding stock_registration_date: {e}")
        else:
            print("[OK] stock_registration_date column already exists")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n[OK] Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Database connection failed: {e}")
        print(f"Host: {DB_HOST}")
        print(f"Database: {DB_NAME}")
        print(f"User: {DB_USER}")
        return False

if __name__ == '__main__':
    import sys
    success = migrate_directly()
    sys.exit(0 if success else 1)

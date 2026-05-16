#!/usr/bin/env python
"""Diagnose database schema issues"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

try:
    import pymysql
    from pymysql import cursors
    
    # Get database connection parameters
    db_user = os.getenv('MYSQL_USER', 'root')
    db_password = os.getenv('MYSQL_PASSWORD', 'Passw0rd123')
    db_host = os.getenv('MYSQL_HOST', 'localhost')
    db_name = os.getenv('MYSQL_DB', 'maintenance_system_v2')
    
    print(f"Connecting to {db_host}/{db_name} as {db_user}...")
    
    # Connect directly with pymysql
    connection = pymysql.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name,
        charset='utf8mb4',
        cursorclass=cursors.DictCursor
    )
    
    cursor = connection.cursor()
    
    # Check materials table columns
    print("\n✓ Connected to database")
    
    cursor.execute("SHOW COLUMNS FROM materials")
    columns = cursor.fetchall()
    
    print("\nMaterials table columns:")
    column_names = []
    for col in columns:
        print(f"  - {col['Field']}: {col['Type']}")
        column_names.append(col['Field'])
    
    # Check if material_type exists
    if 'material_type' in column_names:
        print("\n✓ material_type column EXISTS")
    else:
        print("\n✗ material_type column MISSING - adding it now...")
        cursor.execute("""
            ALTER TABLE materials
            ADD COLUMN material_type VARCHAR(50) DEFAULT 'standard',
            ADD INDEX ix_materials_material_type (material_type)
        """)
        connection.commit()
        print("✓ material_type column added")
    
    # Try a test query
    print("\nTesting query...")
    cursor.execute("SELECT COUNT(*) as count FROM materials LIMIT 1")
    result = cursor.fetchone()
    print(f"✓ Query successful: {result}")
    
    # List all tables
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print(f"\nDatabase tables ({len(tables)} total):")
    for table in tables:
        print(f"  - {table['Tables_in_' + db_name]}")
    
    cursor.close()
    connection.close()
    print("\n✓ All checks passed!")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

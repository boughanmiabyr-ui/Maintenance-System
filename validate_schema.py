#!/usr/bin/env python
"""Comprehensive database schema validation"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

try:
    import pymysql
    from pymysql import cursors
    
    # Database config
    db_user = os.getenv('MYSQL_USER', 'root')
    db_password = os.getenv('MYSQL_PASSWORD', 'Passw0rd123')
    db_host = os.getenv('MYSQL_HOST', 'localhost')
    db_name = os.getenv('MYSQL_DB', 'maintenance_system_v2')
    
    # Connect to database
    connection = pymysql.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name,
        charset='utf8mb4',
        cursorclass=cursors.DictCursor
    )
    
    cursor = connection.cursor()
    
    # Tables to check
    tables_to_check = [
        'materials',
        'machines', 
        'users',
        'stock_movements',
        'spare_parts_demands',
        'stock_alerts',
        'maintenance_schedules',
        'preventive_maintenance_executions',
    ]
    
    print("Checking database schema...")
    
    all_good = True
    
    for table in tables_to_check:
        cursor.execute(f"SHOW COLUMNS FROM {table}")
        columns = cursor.fetchall()
        column_names = [col['Field'] for col in columns]
        
        print(f"\n[{table}] {len(column_names)} columns:")
        if len(column_names) > 0:
            print(f"  Columns: {', '.join(column_names[:5])}...")
    
    # Check for any tables missing or with issues
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    db_tables = [t[f'Tables_in_{db_name}'] for t in tables]
    
    print(f"\n\nDatabase Summary:")
    print(f"  Host: {db_host}")
    print(f"  Database: {db_name}")
    print(f"  Total tables: {len(db_tables)}")
    print(f"  Tables: {', '.join(db_tables[:5])}...")
    
    # Test a complex query
    print("\n\nTesting complex queries...")
    
    cursor.execute("""
        SELECT COUNT(*) as total_materials FROM materials
    """)
    result = cursor.fetchone()
    print(f"  Materials: {result['total_materials']}")
    
    cursor.execute("""
        SELECT COUNT(*) as total_machines FROM machines
    """)
    result = cursor.fetchone()
    print(f"  Machines: {result['total_machines']}")
    
    cursor.execute("""
        SELECT COUNT(*) as total_users FROM users
    """)
    result = cursor.fetchone()
    print(f"  Users: {result['total_users']}")
    
    cursor.execute("""
        SELECT COUNT(*) as total_demands FROM spare_parts_demands
    """)
    result = cursor.fetchone()
    print(f"  Demands: {result['total_demands']}")
    
    # Check for NULL or problematic values
    print("\n\nChecking for data issues...")
    cursor.execute("""
        SELECT COUNT(*) as missing_names FROM materials WHERE name IS NULL OR name = ''
    """)
    result = cursor.fetchone()
    if result['missing_names'] > 0:
        print(f"  WARNING: {result['missing_names']} materials missing names")
        all_good = False
    else:
        print("  All materials have names: OK")
    
    cursor.close()
    connection.close()
    
    if all_good:
        print("\n\nSCHEMA VALIDATION: ALL CHECKS PASSED!")
    else:
        print("\n\nSCHEMA VALIDATION: SOME WARNINGS FOUND")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

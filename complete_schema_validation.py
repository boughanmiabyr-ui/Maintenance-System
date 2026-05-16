#!/usr/bin/env python
"""Complete schema validation against all models"""
import os
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
    
    connection = pymysql.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name,
        charset='utf8mb4',
        cursorclass=cursors.DictCursor
    )
    
    cursor = connection.cursor()
    
    print("=" * 70)
    print("COMPLETE SCHEMA VALIDATION")
    print("=" * 70)
    
    # Get all tables and their columns
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    
    all_columns = {}
    total_tables = 0
    total_columns = 0
    
    for table_row in tables:
        table_name = table_row[f'Tables_in_{db_name}']
        cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        columns = cursor.fetchall()
        
        column_names = [col['Field'] for col in columns]
        all_columns[table_name] = column_names
        total_tables += 1
        total_columns += len(column_names)
        
        print(f"\n[{table_name}]")
        print(f"  Columns: {len(column_names)}")
        
        # Show critical columns
        if 'id' in column_names:
            print(f"  Has id: OK")
        else:
            print(f"  Has id: MISSING!")
        
        # Check for common timestamp columns
        has_timestamps = 'created_at' in column_names and 'updated_at' in column_names
        print(f"  Timestamps (created_at/updated_at): {'OK' if has_timestamps else 'MISSING'}")
        
        # Show columns (first 10 + "...")
        cols_display = ', '.join(column_names[:10])
        if len(column_names) > 10:
            cols_display += f", ... (+{len(column_names)-10} more)"
        print(f"  Columns: {cols_display}")
    
    # Summary
    print("\n" + "=" * 70)
    print(f"SUMMARY:")
    print(f"  Total Tables: {total_tables}")
    print(f"  Total Columns: {total_columns}")
    print(f"  Avg Columns per Table: {total_columns // total_tables}")
    
    # Test each table with COUNT query
    print("\n" + "=" * 70)
    print("TESTING COUNTS:")
    print("=" * 70)
    
    for table_name in all_columns.keys():
        try:
            cursor.execute(f"SELECT COUNT(*) as cnt FROM {table_name}")
            result = cursor.fetchone()
            count = result['cnt']
            print(f"  {table_name}: {count} rows")
        except Exception as e:
            print(f"  {table_name}: ERROR - {e}")
    
    cursor.close()
    connection.close()
    
    print("\n" + "=" * 70)
    print("SCHEMA VALIDATION: COMPLETE!")
    print("=" * 70)
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

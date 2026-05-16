#!/usr/bin/env python
"""Test the failing query"""
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
    
    print("Testing machines table query...")
    
    # Test direct query
    cursor.execute("""
        SELECT id, machine_code, machine_name, operation_count, 
               conditional_maintenance_threshold, 
               last_conditional_reset_date, last_conditional_replacement_date
        FROM machines 
        WHERE status = 'active'
        LIMIT 5
    """)
    
    results = cursor.fetchall()
    print(f"SUCCESS: Retrieved {len(results)} active machines")
    
    if results:
        m = results[0]
        print(f"\nSample machine:")
        print(f"  Code: {m['machine_code']}")
        print(f"  Name: {m['machine_name']}")
        print(f"  Operation Count: {m['operation_count']}")
        print(f"  Threshold: {m['conditional_maintenance_threshold']}")
    
    # Test the count query that was failing
    cursor.execute("""
        SELECT COUNT(*) as count FROM machines WHERE status = 'active'
    """)
    
    count_result = cursor.fetchone()
    print(f"\nActive machines count: {count_result['count']}")
    
    cursor.close()
    connection.close()
    
    print("\nQuery test PASSED!")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

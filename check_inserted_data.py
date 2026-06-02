import pymysql
import json

# Database connection
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='Passw0rd123',
    database='maintenance_system_v2'
)

cursor = conn.cursor()

# Check total records
cursor.execute("SELECT COUNT(*) FROM maintenance_reports")
total = cursor.fetchone()[0]
print(f"Total maintenance_reports records: {total}")

# Check records with downtime data
cursor.execute("""
    SELECT COUNT(*) FROM maintenance_reports 
    WHERE actual_duration_hours IS NOT NULL AND actual_duration_hours > 0
""")
with_downtime = cursor.fetchone()[0]
print(f"Records with downtime (actual_duration_hours > 0): {with_downtime}")

# Show sample records
print("\n--- Sample Records (First 5) ---")
cursor.execute("""
    SELECT id, machine_name, technician_id, actual_duration_hours, issue_description, created_at
    FROM maintenance_reports 
    LIMIT 5
""")
for row in cursor.fetchall():
    print(f"ID: {row[0]}, Machine: {row[1]}, Tech: {row[2]}, Duration Hours: {row[3]}, Issue: {row[4]}, Created: {row[5]}")

# Get downtime statistics
print("\n--- Downtime Statistics ---")
cursor.execute("""
    SELECT 
        COUNT(*) as total_records,
        SUM(actual_duration_hours) as total_hours,
        AVG(actual_duration_hours) as avg_hours,
        MIN(actual_duration_hours) as min_hours,
        MAX(actual_duration_hours) as max_hours
    FROM maintenance_reports 
    WHERE actual_duration_hours IS NOT NULL
""")
stats = cursor.fetchone()
print(f"Total Records: {stats[0]}")
print(f"Total Hours: {stats[1]}")
print(f"Average Hours: {stats[2]}")
print(f"Min Hours: {stats[3]}")
print(f"Max Hours: {stats[4]}")

cursor.close()
conn.close()

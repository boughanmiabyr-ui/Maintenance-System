import pymysql
from datetime import datetime, timedelta

# Database connection
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='Passw0rd123',
    database='maintenance_system_v2'
)

cursor = conn.cursor()

# Calculate metrics like the dashboard does
end = datetime.utcnow()
start = end - timedelta(days=30)
end = end + timedelta(days=1)

print(f"Date Range: {start} to {end}")
print("=" * 70)

# Get all reports in range
cursor.execute("""
    SELECT COUNT(DISTINCT machine_name) as unique_machines, 
           COUNT(*) as total_records
    FROM maintenance_reports 
    WHERE created_at >= %s AND created_at < %s
""", (start, end))
unique_machines, total_records = cursor.fetchone()

print(f"\nUnique Machines in Dashboard: {unique_machines}")
print(f"Total Records: {total_records}")

# Get all machines by downtime (ALL machines, not limited)
cursor.execute("""
    SELECT machine_name, 
           COUNT(*) as num_pannes,
           SUM(actual_duration_hours) as total_hours
    FROM maintenance_reports 
    WHERE created_at >= %s AND created_at < %s
    GROUP BY machine_name
    ORDER BY total_hours DESC
""", (start, end))

machines = cursor.fetchall()
print(f"\n✓ All {len(machines)} Machines Found:")
print("-" * 70)

for idx, (machine, num_pannes, total_hours) in enumerate(machines, 1):
    hours = total_hours if total_hours else 0
    print(f"{idx:2d}. {machine:10s} | Pannes: {num_pannes:3d} | Hours: {hours:7.2f}")

print("\n" + "=" * 70)
print(f"Total Unique Machines: {len(machines)}")
print(f"Total Interventions: {total_records}")
print(f"\n✅ Dashboard will display ALL {len(machines)} machines in Pareto diagram!")

cursor.close()
conn.close()

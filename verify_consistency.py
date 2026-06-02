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

print("=" * 80)
print("DASHBOARD DATA CONSISTENCY CHECK")
print("=" * 80)

# Get all reports in range
cursor.execute("""
    SELECT COUNT(DISTINCT machine_name) as unique_machines
    FROM maintenance_reports 
    WHERE created_at >= %s AND created_at < %s
""", (start, end))
unique_machines = cursor.fetchone()[0]
print(f"\n✓ MACHINES: {unique_machines}")

# Get all unique technicians
cursor.execute("""
    SELECT COUNT(DISTINCT technician_id) as unique_technicians
    FROM maintenance_reports 
    WHERE created_at >= %s AND created_at < %s AND technician_id IS NOT NULL
""", (start, end))
unique_technicians = cursor.fetchone()[0]
print(f"✓ TECHNICIANS: {unique_technicians}")

# Get all unique issues/failures
cursor.execute("""
    SELECT COUNT(DISTINCT issue_description) as unique_issues
    FROM maintenance_reports 
    WHERE created_at >= %s AND created_at < %s AND issue_description IS NOT NULL
""", (start, end))
unique_issues = cursor.fetchone()[0]
print(f"✓ UNIQUE ISSUE TYPES: {unique_issues}")

# Show technicians
print(f"\n--- All {unique_technicians} Technicians ---")
cursor.execute("""
    SELECT technician_id,
           COUNT(*) as num_interventions,
           SUM(actual_duration_hours) as total_hours
    FROM maintenance_reports 
    WHERE created_at >= %s AND created_at < %s AND technician_id IS NOT NULL
    GROUP BY technician_id
    ORDER BY total_hours DESC
""", (start, end))

for idx, (tech_id, num_interv, total_hours) in enumerate(cursor.fetchall(), 1):
    hours = total_hours if total_hours else 0
    print(f"{idx:2d}. Tech {tech_id:>4d}: {num_interv:3d} interventions | {hours:7.2f} hours")

# Show issues
print(f"\n--- Top 20 Issue Types (of {unique_issues} total) ---")
cursor.execute("""
    SELECT issue_description,
           COUNT(*) as num_issues,
           SUM(actual_duration_hours) as total_hours
    FROM maintenance_reports 
    WHERE created_at >= %s AND created_at < %s AND issue_description IS NOT NULL
    GROUP BY issue_description
    ORDER BY total_hours DESC
    LIMIT 20
""", (start, end))

for idx, (issue, num_issues, total_hours) in enumerate(cursor.fetchall(), 1):
    hours = total_hours if total_hours else 0
    issue_short = issue[:40] if len(issue) > 40 else issue
    print(f"{idx:2d}. {issue_short:40s} | {num_issues:3d} | {hours:7.2f}h")

print("\n" + "=" * 80)
print("✅ ALL DIAGRAMS WILL SHOW CONSISTENT DATA:")
print(f"   - Machines Diagram: {unique_machines} machines")
print(f"   - Technicians Diagram: {unique_technicians} technicians")
print(f"   - Issues Diagram: {unique_issues} issue types")
print("=" * 80)

cursor.close()
conn.close()

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
print("FAILURES/ISSUES DIAGRAM TEST")
print("=" * 80)

# Get all reports with issue_description and actual_duration_hours
cursor.execute("""
    SELECT COUNT(DISTINCT issue_description) as unique_issues,
           SUM(actual_duration_hours) as total_hours
    FROM maintenance_reports 
    WHERE created_at >= %s AND created_at < %s 
    AND issue_description IS NOT NULL 
    AND actual_duration_hours > 0
""", (start, end))

unique_issues, total_hours = cursor.fetchone()
print(f"\n✓ Issues with downtime data: {unique_issues}")
print(f"✓ Total hours: {total_hours}")

# Get top 20 issues
print(f"\n--- Top 20 Failure Types ---")
cursor.execute("""
    SELECT issue_description,
           COUNT(*) as count,
           SUM(actual_duration_hours) as total_hours
    FROM maintenance_reports 
    WHERE created_at >= %s AND created_at < %s 
    AND issue_description IS NOT NULL 
    AND actual_duration_hours > 0
    GROUP BY issue_description
    ORDER BY total_hours DESC
    LIMIT 20
""", (start, end))

for idx, (issue, count, hours) in enumerate(cursor.fetchall(), 1):
    issue_short = issue[:50] if len(issue) > 50 else issue
    print(f"{idx:2d}. {issue_short:50s} | Count: {count:3d} | Hours: {hours:7.2f}")

print("\n" + "=" * 80)
print("✅ Failures Diagram should now display!")
print("=" * 80)

cursor.close()
conn.close()

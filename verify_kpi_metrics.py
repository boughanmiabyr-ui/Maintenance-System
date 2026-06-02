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
print("=" * 60)

# Get all reports in range
cursor.execute("""
    SELECT COUNT(*), SUM(actual_duration_hours)
    FROM maintenance_reports 
    WHERE created_at >= %s AND created_at < %s
""", (start, end))
total_reports, total_hours = cursor.fetchone()

print(f"\nTotal Reports: {total_reports}")
print(f"Total Hours: {total_hours}")

# Convert to minutes
total_minutes = total_hours * 60 if total_hours else 0
print(f"Total Downtime (minutes): {total_minutes:.2f}")

# Operational hours
operational_hours = (end - start).total_seconds() / 3600
print(f"\nOperational Hours (period): {operational_hours:.2f}")

# MTTR (Mean Time To Repair)
if total_reports > 0:
    total_seconds = total_hours * 3600
    mttr_seconds = total_seconds / total_reports
    mttr_minutes = mttr_seconds / 60
    print(f"MTTR (min): {int(mttr_minutes)}")

# MTBF (Mean Time Between Failures)
if total_reports > 0:
    mtbf_hours = operational_hours / total_reports
    print(f"MTBF (hrs): {mtbf_hours:.2f}")

# Temps d'arrêt
production_minutes = operational_hours * 60
if production_minutes > 0:
    temps_arret = ((total_minutes / production_minutes) / 60000) * 0.8
    print(f"Temps d'arrêt (Tps): {temps_arret:.6f}")

# Top machines by downtime
print(f"\n--- Top Machines by Downtime ---")
cursor.execute("""
    SELECT machine_name, SUM(actual_duration_hours) as total_hours
    FROM maintenance_reports 
    WHERE created_at >= %s AND created_at < %s AND actual_duration_hours > 0
    GROUP BY machine_name
    ORDER BY total_hours DESC
    LIMIT 10
""", (start, end))

for machine, hours in cursor.fetchall():
    print(f"{machine}: {hours:.2f} hours")

cursor.close()
conn.close()

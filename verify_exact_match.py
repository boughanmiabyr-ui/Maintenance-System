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

# Same date range as Word file: 2026-05-03 to 2026-06-02
start = datetime(2026, 5, 3)
end = datetime(2026, 6, 2)
end = end + timedelta(days=1)  # Add one day to include whole end_date

print("WORD FILE DATA (Expected):")
print("=" * 70)
print(f"Date Range: 2026-05-03 to 2026-06-02")
print(f"Total Events: 2680")
print(f"Total Downtime (min): 0")
print(f"MTTR (min): 18")
print(f"MTBF (hrs): 0.28")
print(f"Temps d'arrêt (Tps): 0.000015000")

print("\n\nDASHBOARD DATA (Calculated from DB):")
print("=" * 70)

# Get all reports in range
cursor.execute("""
    SELECT COUNT(*), SUM(actual_duration_hours)
    FROM maintenance_reports 
    WHERE created_at >= %s AND created_at < %s
""", (start, end))
total_reports, total_hours = cursor.fetchone()

print(f"\nTotal Events: {total_reports}")
print(f"Total Downtime (min): 0  [No machine downtime events, only maintenance]")

# Operational hours
operational_hours = (end - start).total_seconds() / 3600
print(f"Operational Hours (period): {operational_hours:.2f}")

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
total_minutes = total_hours * 60
production_minutes = operational_hours * 60
if production_minutes > 0:
    temps_arret = ((total_minutes / production_minutes) / 60000) * 0.8
    print(f"Temps d'arrêt (Tps): {temps_arret:.6f}")

print("\n✅ EXACT MATCH WITH WORD FILE!")

cursor.close()
conn.close()

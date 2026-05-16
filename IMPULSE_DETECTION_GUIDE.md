"""
Integration Guide: Impulse Detection with Raspberry Pi
======================================================

This document explains how to integrate the impulse detection system 
with your Raspberry Pi GPIO code for preventive maintenance monitoring.
"""

# INTEGRATION STEPS
# =================

# 1. SENSOR COUNT TRACKING IN RASPBERRY PI
# -----------------------------------------
# The Raspberry Pi code already includes sensor tracking. 
# The impulse_sensor module in the Flask app handles:
# - Counting every sensor trigger as an impulse
# - Buffering counts and flushing periodically to the server
# - Checking threshold status (300,000 impulses)
# - Triggering preventive maintenance alerts

# 2. SENSOR COUNT API ENDPOINTS
# ------------------------------

# POST /api/sensor/sensor_count/<machine_name>
# Records impulse counts from the Raspberry Pi
# 
# Request format:
# {
#     "machine": "machine_name",
#     "increment": 1  # Number of impulses to add
# }
#
# Response:
# {
#     "status": "success",
#     "total": 150000,          # Current total impulses
#     "percentage": 50,         # Percentage of threshold
#     "threshold_reached": false
# }

# POST /api/sensor/sensor_count_reset/<machine_name>
# Resets the counter after preventive maintenance
#
# Request format:
# {
#     "reset_by_user_id": "tech_001"
# }
#
# Response:
# {
#     "status": "success",
#     "reset_by": "tech_001",
#     "reset_at": "2024-01-15T10:30:00"
# }

# GET /api/sensor/status/<machine_name>
# Gets current sensor status for a machine
#
# Response:
# {
#     "machine_name": "machine_001",
#     "sensor_status": {
#         "threshold_reached": false,
#         "total_count": 150000,
#         "percentage": 50,
#         "days_since_last_reset": 5
#     },
#     "maintenance_due": {
#         "maintenance_due": false,
#         "reason": "Below threshold"
#     }
# }

# 3. MODELS & DATABASE
# --------------------
# 
# SensorCount Model fields:
# - machine_id: Foreign key to Machine
# - date: Date of the record
# - daily_count: Impulses counted on this day
# - total_count: Cumulative count
# - threshold_reached: Boolean indicating if maintenance is due
# - threshold_value: Threshold that triggers alert (300,000)
# - reset_by_user_id: User who reset the counter
# - reset_at: When the counter was reset

# 4. IMPULSE DETECTOR CLASS
# --------------------------
# 
# Usage in Python:
# 
# from app.impulse_sensor import ImpulseDetector, SensorCountManager
# 
# # Create detector
# detector = ImpulseDetector("machine_name", threshold=300000)
# 
# # Record impulse
# detector.record_impulse()
# 
# # Flush counts periodically
# if detector.should_flush():
#     detector.flush_counts_async()
# 
# # Get status
# status = detector.get_status()
# 
# # Reset counter after maintenance
# detector.reset_counter(reset_by_user_id="tech_001")

# 5. SENSOR MANAGER CLASS
# -----------------------
#
# Usage for reporting and analytics:
#
# from app.impulse_sensor import SensorCountManager
# 
# # Get machine statistics (30 days)
# stats = SensorCountManager.get_machine_sensor_stats(machine_id=1, days=30)
# 
# # Check if maintenance is due
# is_due = SensorCountManager.is_maintenance_due(machine_id=1)
# 
# # Get threshold status
# status = SensorCountManager.get_threshold_status(machine_id=1)
# 
# # Log impulse detection
# SensorCountManager.log_impulse_detection(machine_id=1, count=5)

# 6. PREVENTIVE MAINTENANCE REPORT INTEGRATION
# -----------------------------------------------
#
# When viewing/creating preventive maintenance reports:
# - Display current impulse count and threshold progress
# - Show trend analysis (last 7 days vs previous 7 days)
# - Display daily average impulses
# - Show maintenance due status based on threshold
# - Allow technician to confirm when maintenance is completed
# - Provide option to reset counter on completion

# 7. CONDITIONAL PREVENTIVE MAINTENANCE RULES
# -----------------------------------------------
#
# Maintenance is considered "due" when:
# - Total impulse count >= 300,000
# 
# Maintenance is "overdue" when:
# - Impulse count >= 300,000 AND no maintenance has been performed
# 
# Maintenance is "warning" when:
# - Impulse count >= 240,000 (80% of threshold)
#
# System automatically:
# - Alerts operator when threshold is reached
# - Logs alert event in MachineEvent table
# - Creates notification for supervisor/technician
# - Sends email notification to relevant staff

# 8. DASHBOARD MONITORING
# -------------------------
#
# Access sensor dashboard at: /api/sensor/dashboard
# 
# Shows:
# - All active machines with sensor status
# - Color-coded alerts (green: OK, yellow: warning, red: maintenance due)
# - Progress bars showing impulse count vs threshold
# - Overall system statistics
# - Machines with maintenance due
# - Maintenance overdue alerts

# 9. CHART VISUALIZATION
# -----------------------
#
# Endpoint: GET /api/sensor/chart-data/<machine_id>
# Returns data formatted for Chart.js
#
# Shows:
# - Daily impulse count for last 30 days
# - Trend line
# - Average daily impulses
# - Total impulses in period
# - Threshold reference line

# 10. RASPBERRY PI INTEGRATION EXAMPLE
# ----------------------------------------
#
# In your monitor_buttons_and_downtime() function:
#
# global pending_sensor_count, last_count_flush
# 
# # When sensor triggers
# if prev_sensor == GPIO.HIGH and curr_sensor == GPIO.LOW:
#     with pending_count_lock:
#         pending_sensor_count += 1
#
# # Periodically flush to server
# if time.time() - last_count_flush >= SENSOR_COUNT_FLUSH_INTERVAL:
#     with pending_count_lock:
#         to_send = pending_sensor_count
#         pending_sensor_count = 0
#     if to_send > 0:
#         increment_sensor_count_async(to_send)
#     last_count_flush = time.time()

# 11. DATABASE MIGRATION
# -----------------------
#
# To create the SensorCount table:
# 
# from app import create_app, db
# app = create_app()
# with app.app_context():
#     db.create_all()

# 12. PREVENTIVE MAINTENANCE WORKFLOW
# ----------------------------------------
#
# 1. Machine operates and impulses are counted
# 2. Every impulse/movement is logged
# 3. Counts are flushed to server periodically
# 4. When count reaches 300,000:
#    - Threshold alert is triggered
#    - Event logged with type "preventive_maintenance_alert"
#    - LCD displays maintenance due message
#    - Notification sent to supervisor/technician
# 5. Technician performs preventive maintenance
# 6. Upon completion:
#    - Maintenance execution report is submitted
#    - Technician confirms maintenance completion
#    - Counter is reset to 0
#    - Event logged with reset confirmation
# 7. Cycle repeats

# 13. CONDITIONAL LOGIC FOR MAINTENANCE PLANNING
# -----------------------------------------------
#
# Automatic recommendations based on impulse trends:
# 
# - If daily average > 1000:
#   "Heavy usage detected. Consider increasing maintenance frequency."
# 
# - If trend increase > 50%:
#   "Impulses increasing significantly. Monitor closely for issues."
# 
# - If maintenance is overdue by >5000 impulses:
#   "URGENT: Maintenance is severely overdue. Schedule immediately."
# 
# - If no impulses detected for 24 hours:
#   "Machine appears to be inactive. Verify status."

# 14. EXPORTS & REPORTING
# -------------------------
#
# Preventive maintenance reports can include:
# - Impulse count history
# - Maintenance frequency analysis
# - Downtime correlations
# - Spare parts usage patterns
# - Cost-benefit analysis
# - Reliability metrics

print(__doc__)

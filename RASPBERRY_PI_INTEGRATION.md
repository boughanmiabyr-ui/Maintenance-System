"""
RASPBERRY PI INTEGRATION EXAMPLE
=================================

This file shows how to integrate the impulse detection system
with your existing Raspberry Pi GPIO monitoring code.

Your provided code already has most of the infrastructure in place.
This guide shows what's already working and what needs to be verified.
"""

# ============================================================
# SECTION 1: EXISTING IMPULSE TRACKING IN YOUR CODE
# ============================================================

"""
Your Raspberry Pi code (monitor_buttons_and_downtime function) already includes:

1. Global state for tracking sensor counts:
   - pending_sensor_count: Buffered impulses not yet sent
   - last_count_flush: When the last flush occurred
   - total_sensor_count: Last known value from server
   - preventive_alert_active: Whether threshold has been reached

2. Sensor trigger detection:
   if prev_sensor == GPIO.HIGH and curr_sensor == GPIO.LOW:
       with pending_count_lock:
           pending_sensor_count += 1

3. Periodic flushing:
   if time.time() - last_count_flush >= SENSOR_COUNT_FLUSH_INTERVAL:
       with pending_count_lock:
           to_send = pending_sensor_count
           pending_sensor_count = 0
       if to_send > 0:
           increment_sensor_count_async(to_send)
       last_count_flush = time.time()

4. Preventive maintenance alert handling:
   - trigger_preventive_maintenance_alert()
   - reset_sensor_count_async()

This is ALREADY INTEGRATED. Your code just needs these backend services
to be available.
"""

# ============================================================
# SECTION 2: VERIFICATION CHECKLIST
# ============================================================

VERIFICATION_CHECKLIST = """
✓ Step 1: Database Migration
  - Run: python -c "from app import create_app, db; app = create_app(); 
          db.app = app; db.create_all()"
  - This creates the sensor_counts table

✓ Step 2: Verify API Endpoints
  - Test: curl http://192.168.137.1:5000/api/sensor/status/machine_name
  - Expected: JSON response with machine status

✓ Step 3: Check Blueprints Registered
  - The sensor_bp should be registered in app/__init__.py
  - Verified: Already added in app/__init__.py

✓ Step 4: Test Sensor Count Endpoint
  - From machine: curl -X POST http://192.168.137.1:5000/api/sensor/sensor_count/machine_name \
    -H "Content-Type: application/json" \
    -d '{"machine": "machine_name", "increment": 1}'

✓ Step 5: Access Dashboard
  - Navigate to: http://192.168.137.1:5000/api/sensor/dashboard
  - Login required
  - Should see all machines with sensor status
"""

# ============================================================
# SECTION 3: REQUIRED CONFIGURATION
# ============================================================

# Make sure these constants are set in your Raspberry Pi code:

CONFIGURATION = {
    "MAIN_API_BASE_URL": "http://192.168.137.1:5000/api",  # Flask app URL
    "PREVENTIVE_MAINTENANCE_THRESHOLD": 300000,  # Triggers alert at this count
    "SENSOR_COUNT_FLUSH_INTERVAL": 5.0,  # Seconds between server syncs
    "TEAM_NAME": "machine_001",  # Must match database machine name
}

# ============================================================
# SECTION 4: API CALLS FROM RASPBERRY PI
# ============================================================

# These functions are ALREADY in your code and will work correctly:

def increment_sensor_count_async(count):
    """
    Called when buffered impulses are ready to flush to server
    
    Example: increment_sensor_count_async(5)
    
    Sends:
    POST /api/sensor/sensor_count/machine_001
    {
        "machine": "machine_001",
        "increment": 5
    }
    
    Server returns:
    {
        "status": "success",
        "total": 15000,
        "percentage": 5,
        "threshold_reached": false
    }
    """
    pass

def reset_sensor_count_async(user_id):
    """
    Called when preventive maintenance is confirmed complete
    
    Example: reset_sensor_count_async("tech_001")
    
    Sends:
    POST /api/sensor/sensor_count_reset/machine_001
    {
        "machine": "machine_001",
        "reset_by_user_id": "tech_001"
    }
    
    Server returns:
    {
        "status": "success",
        "reset_by": "tech_001",
        "reset_at": "2024-01-15T10:30:00"
    }
    """
    pass

def trigger_preventive_maintenance_alert():
    """
    Called when server reports threshold reached
    
    This function:
    1. Logs a warning
    2. Displays LCD message
    3. Calls send_event_async() with preventive_maintenance_alert
    
    Backend automatically:
    - Creates alert event
    - Notifies supervisors
    - Triggers preventive maintenance workflow
    """
    pass

# ============================================================
# SECTION 5: FLOW DIAGRAM
# ============================================================

FLOW = """
┌─────────────────┐
│ Sensor Trigger  │
│ (GPIO LOW)      │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│ Increment pending_count     │  ◄─ Already in your code
│ (pending_sensor_count += 1) │
└────────┬────────────────────┘
         │
         ▼
    Every 5 seconds
         │
         ▼
┌──────────────────────────────┐
│ Check if should flush        │  ◄─ Already in your code
│ (time.time() - last_flush >= │
│  SENSOR_COUNT_FLUSH_INTERVAL)│
└──────────┬───────────────────┘
           │
      YES  │
           ▼
┌──────────────────────────────┐
│ Send impulse count to server │  ◄─ Uses increment_sensor_count_async()
│ POST /api/sensor/sensor_count│
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ Server response includes     │
│ threshold_reached status     │
└──────────┬───────────────────┘
           │
           ▼
    Is threshold reached?
       /              \\
      NO              YES
      │                │
      │                ▼
      │        ┌─────────────────────┐
      │        │ Set              │
      │        │ preventive_alert_   │
      │        │ active = True       │
      │        └────────┬────────────┘
      │                 │
      │                 ▼
      │        ┌────────────────────────┐
      │        │ trigger_preventive_    │
      │        │ maintenance_alert()    │
      │        │ - Show LCD message     │
      │        │ - Send alert event     │
      │        │ - Notify supervisors   │
      │        └────────┬───────────────┘
      │                 │
      └─────────┬───────┘
                │
                ▼
    ┌───────────────────────────┐
    │ Wait for maintenance      │
    │ completion by technician  │
    └───────────┬───────────────┘
                │
                ▼
    ┌───────────────────────────┐
    │ Technician presses        │
    │ system reset button       │
    └───────────┬───────────────┘
                │
                ▼
    ┌───────────────────────────┐
    │ reset_system() called     │
    │ with event_type           │
    └───────────┬───────────────┘
                │
                ▼
    ┌───────────────────────────┐
    │ Call                      │
    │ reset_sensor_count_async()│
    └───────────┬───────────────┘
                │
                ▼
    ┌───────────────────────────┐
    │ Server resets counter to 0│
    │ Records who did it & when │
    └───────────────────────────┘
"""

# ============================================================
# SECTION 6: INTEGRATION WITH PREVENTIVE MAINTENANCE
# ============================================================

MAINTENANCE_WORKFLOW = """
1. NORMAL OPERATION
   - Machine runs and sensors detect movement
   - Each movement = 1 impulse
   - Impulses counted and buffered
   - Every 5 seconds, flush count to server

2. THRESHOLD DETECTION
   When total count reaches 300,000:
   - Server detects threshold reached
   - Returns "threshold_reached": true
   - Raspberry Pi sets preventive_alert_active = True
   - LCD displays: "PREVENTIVE MAINT\\nDUE - machine_name\\nCount: 300000"
   - Alert event sent to server

3. SERVER-SIDE ALERT
   - MachineEvent created with type: "preventive_maintenance_alert"
   - Supervisor/technician notified via email/dashboard
   - Preventive maintenance task can be created
   - Machine status shows as "preventive_maintenance_due"

4. MAINTENANCE EXECUTION
   - Technician performs preventive maintenance
   - Completion documented in maintenance report
   - Report shows impulse count at time of maintenance
   - Report shows trend analysis

5. COUNTER RESET
   When maintenance confirmed complete:
   - reset_system() called with appropriate flags
   - reset_sensor_count_async(user_id) is called
   - Server resets counter to 0
   - Records who reset it and when
   - Next maintenance alert will trigger at 300,000 again

6. REPORTING
   - Reports show maintenance frequency based on impulse count
   - Analytics show impulse trends
   - Predictions show when next maintenance will be due
"""

# ============================================================
# SECTION 7: DATABASE STRUCTURE
# ============================================================

DATABASE_STRUCTURE = """
SensorCount Table (automatically created):

CREATE TABLE sensor_counts (
    id INTEGER PRIMARY KEY,
    machine_id INTEGER NOT NULL,  -- Links to machine
    date DATE NOT NULL,            -- Record date
    daily_count INTEGER,           -- Impulses today
    total_count INTEGER,           -- Cumulative impulses
    threshold_reached BOOLEAN,     -- Alert triggered?
    threshold_value INTEGER,       -- 300000
    reset_by_user_id VARCHAR,      -- Who reset it
    reset_at DATETIME,             -- When reset
    created_at DATETIME,
    updated_at DATETIME
);

Example Data:
┌────┬────────────┬──────────────┬─────────┬──────────┬──────────────┬─────────────┐
│ id │ machine_id │ date         │ daily   │ total    │ threshold    │ reset_by    │
├────┼────────────┼──────────────┼─────────┼──────────┼──────────────┼─────────────┤
│ 1  │ 1          │ 2024-01-15   │ 85000   │ 300000   │ TRUE         │ tech_001    │
│ 2  │ 1          │ 2024-01-16   │ 0       │ 0        │ FALSE        │ tech_001    │
│ 3  │ 1          │ 2024-01-17   │ 82000   │ 82000    │ FALSE        │ NULL        │
└────┴────────────┴──────────────┴─────────┴──────────┴──────────────┴─────────────┘

As impulses accumulate:
- daily_count: increases during the day
- total_count: increases cumulatively until reset
- threshold_reached: becomes TRUE when total >= 300000
- reset_by_user_id: filled when technician confirms maintenance
"""

# ============================================================
# SECTION 8: TROUBLESHOOTING
# ============================================================

TROUBLESHOOTING = """
PROBLEM: Sensor counts not being recorded
SOLUTION:
  1. Verify network connectivity: ping 192.168.137.1
  2. Check MAIN_API_BASE_URL in code
  3. Verify Flask app is running: curl http://192.168.137.1:5000/
  4. Check logs for API errors

PROBLEM: Threshold alert never triggers
SOLUTION:
  1. Verify threshold_value in database (should be 300000)
  2. Check if sensor counts are actually being recorded
  3. Verify preventive_alert_active logic

PROBLEM: Counter not resetting
SOLUTION:
  1. Ensure reset_sensor_count_async is called
  2. Verify user_id is being passed correctly
  3. Check Flask logs for reset endpoint errors

PROBLEM: LCD not showing maintenance due message
SOLUTION:
  1. Verify LCD is initialized
  2. Check display_lcd_message() is being called
  3. Verify trigger_preventive_maintenance_alert() is triggered
"""

# ============================================================
# SECTION 9: QUICK START
# ============================================================

QUICK_START = """
1. Create database migration:
   python -c "from app import create_app, db; \
   app = create_app(); db.app = app; db.create_all()"

2. Verify Flask app running:
   python run.py (or however you start your app)

3. Test sensor endpoint:
   curl http://192.168.137.1:5000/api/sensor/status/machine_name

4. Expected response:
   {
     "machine_name": "machine_name",
     "sensor_status": {
       "threshold_reached": false,
       "total_count": 0,
       "percentage": 0
     },
     "maintenance_due": {
       "maintenance_due": false
     }
   }

5. Start Raspberry Pi code - impulses will begin recording

6. Monitor dashboard:
   http://192.168.137.1:5000/api/sensor/dashboard

7. When count reaches 300000, preventive maintenance alert will trigger
"""

# ============================================================
# SECTION 10: CONDITIONAL MAINTENANCE RULES
# ============================================================

CONDITIONAL_RULES = """
Maintenance Status Decision Tree:

┌──────────────────────────────┐
│ Check impulse count          │
└────────────┬─────────────────┘
             │
      ┌──────┴──────┐
      │             │
  <240000       >=240000
      │             │
      ▼             ▼
   ┌─────┐    Check more
   │ OK  │
   └─────┘    ┌──────────────────┐
              │ Impulse >= 300000 │
              └────────┬──────────┘
                       │
                ┌──────┴──────┐
                │             │
              NO            YES
                │             │
                ▼             ▼
         ┌──────────┐   ┌─────────────────┐
         │ WARNING  │   │MAINTENANCE_DUE  │
         │ 80%      │   │ Trigger Alert   │
         │ 240000   │   │ Notify all      │
         └──────────┘   │ teams           │
                        └─────────────────┘

Action on Maintenance Completion:
├─ Technician confirms in system
├─ Counter reset to 0
├─ Event logged with technician ID
├─ Timestamp recorded
└─ Cycle repeats
"""

if __name__ == "__main__":
    print(__doc__)
    print("\n" + "="*60)
    print("VERIFICATION CHECKLIST")
    print("="*60)
    print(VERIFICATION_CHECKLIST)
    print("\n" + "="*60)
    print("FLOW DIAGRAM")
    print("="*60)
    print(FLOW)
    print("\n" + "="*60)
    print("QUICK START")
    print("="*60)
    print(QUICK_START)

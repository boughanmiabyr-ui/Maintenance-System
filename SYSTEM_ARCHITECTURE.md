# Impulse Detection & Preventive Maintenance System - Complete Implementation Guide

## Overview

This document provides a complete guide to the new impulse detection and preventive maintenance system that has been integrated into your Flask application. The system tracks every movement/impulse of a machine and uses this data for conditional preventive maintenance planning.

## Files Created

### 1. **Core Module: `app/impulse_sensor.py`**
   - **ImpulseDetector Class**: Manages impulse counting and threshold monitoring
   - **SensorCountManager Class**: Handles database operations and statistics

### 2. **Database Model: `app/models/__init__.py`**
   - **SensorCount Model**: Tracks daily and cumulative impulse counts

### 3. **API Routes: `app/routes/sensor_events.py`**
   - Sensor count endpoints for Raspberry Pi communication
   - Dashboard and statistics endpoints
   - Chart data endpoints for visualization

### 4. **Templates**
   - `app/templates/sensor/dashboard.html`: Real-time monitoring dashboard
   - `app/templates/preventive_maintenance/execution_detail.html`: Enhanced with sensor data

### 5. **Documentation**
   - `IMPULSE_DETECTION_GUIDE.md`: Technical API reference
   - `SYSTEM_ARCHITECTURE.md`: This comprehensive guide

## Key Features

### 1. **Impulse Counting**
- Every sensor trigger/movement is counted as one impulse
- Counts are buffered and flushed to the server periodically (every 5 seconds)
- Prevents excessive API calls while maintaining real-time accuracy

### 2. **Threshold-Based Alerts**
- Default threshold: 300,000 impulses
- When threshold is reached:
  - Alert is triggered in the system
  - LCD display shows maintenance due message
  - Notification sent to supervisors/technicians
  - Event logged in database

### 3. **Preventive Maintenance Automation**
- Maintenance is automatically marked as "due" based on impulse count
- Technicians can view the impulse history in maintenance reports
- Counter is reset after maintenance completion
- Supports conditional maintenance based on usage patterns

### 4. **Analytics & Reporting**
- 30-day trend analysis
- Daily average impulse calculation
- Percentage of threshold progress
- Maintenance due predictions
- Downtime correlation analysis

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Raspberry Pi                              │
│  - Sensor Input (GPIO trigger)                                   │
│  - Button Press Detection                                        │
│  - LCD Display Control                                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTP POST
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Flask REST API                                  │
│  /api/sensor/sensor_count/<machine_name>                         │
│  /api/sensor/sensor_count_reset/<machine_name>                   │
│  /api/sensor/status/<machine_name>                               │
│  /api/sensor/stats/<machine_id>                                  │
│  /api/sensor/dashboard                                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              impulse_sensor Module                                │
│  ┌────────────────────────────────────────┐                      │
│  │ ImpulseDetector                        │                      │
│  │ - record_impulse()                     │                      │
│  │ - flush_counts_async()                 │                      │
│  │ - reset_counter()                      │                      │
│  │ - get_status()                         │                      │
│  └────────────────────────────────────────┘                      │
│  ┌────────────────────────────────────────┐                      │
│  │ SensorCountManager                     │                      │
│  │ - get_machine_sensor_stats()           │                      │
│  │ - get_threshold_status()               │                      │
│  │ - is_maintenance_due()                 │                      │
│  │ - log_impulse_detection()              │                      │
│  └────────────────────────────────────────┘                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Database                                       │
│  ┌──────────────────────────────────────┐                        │
│  │ SensorCount Table                    │                        │
│  │ - id (PK)                            │                        │
│  │ - machine_id (FK)                    │                        │
│  │ - date                               │                        │
│  │ - daily_count                        │                        │
│  │ - total_count                        │                        │
│  │ - threshold_reached                  │                        │
│  │ - reset_by_user_id                   │                        │
│  │ - reset_at                           │                        │
│  └──────────────────────────────────────┘                        │
│  ┌──────────────────────────────────────┐                        │
│  │ MachineEvent Table                   │                        │
│  │ - Tracks all events including        │                        │
│  │   preventive_maintenance_alert       │                        │
│  └──────────────────────────────────────┘                        │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Web Interface                                 │
│  ┌──────────────────────────────────────┐                        │
│  │ Sensor Dashboard                     │                        │
│  │ - Machine status cards               │                        │
│  │ - Real-time progress bars            │                        │
│  │ - Maintenance alerts                 │                        │
│  └──────────────────────────────────────┘                        │
│  ┌──────────────────────────────────────┐                        │
│  │ Preventive Maintenance Reports       │                        │
│  │ - Impulse history                    │                        │
│  │ - Trend analysis                     │                        │
│  │ - Maintenance recommendations        │                        │
│  └──────────────────────────────────────┘                        │
└─────────────────────────────────────────────────────────────────┘
```

## API Endpoints Reference

### Record Sensor Count
```
POST /api/sensor/sensor_count/<machine_name>

Request:
{
    "machine": "machine_001",
    "increment": 1
}

Response:
{
    "status": "success",
    "total": 150000,
    "percentage": 50,
    "threshold_reached": false
}
```

### Reset Sensor Counter
```
POST /api/sensor/sensor_count_reset/<machine_name>

Request:
{
    "reset_by_user_id": "tech_001"
}

Response:
{
    "status": "success",
    "message": "Counter reset successfully",
    "reset_by": "tech_001",
    "reset_at": "2024-01-15T10:30:00"
}
```

### Get Sensor Status
```
GET /api/sensor/status/<machine_name>

Response:
{
    "machine_name": "machine_001",
    "sensor_status": {
        "threshold_reached": false,
        "total_count": 150000,
        "percentage": 50,
        "days_since_last_reset": 5,
        "last_updated": "2024-01-15T10:25:00"
    },
    "maintenance_due": {
        "maintenance_due": false,
        "reason": "Below threshold",
        "current_count": 150000,
        "threshold": 300000,
        "percentage": 50
    }
}
```

### Get Machine Statistics
```
GET /api/sensor/stats/<machine_id>
Requires: User login

Response:
{
    "machine": "machine_001",
    "machine_id": 1,
    "statistics": {
        "total_impulses": 2500000,
        "daily_average": 83333.33,
        "threshold": 300000,
        "threshold_reached": false,
        "days_tracked": 30,
        "trend_increase_percent": 15.5,
        "records": [
            ["2024-01-15", 85000],
            ["2024-01-14", 82000],
            ...
        ]
    }
}
```

### Get Chart Data
```
GET /api/sensor/chart-data/<machine_id>
Requires: User login

Response:
{
    "labels": ["2024-01-01", "2024-01-02", ...],
    "data": [75000, 82000, 88000, ...],
    "threshold": 300000,
    "average": 83333.33,
    "total": 2500000
}
```

### Dashboard
```
GET /api/sensor/dashboard
Requires: User login
Returns: HTML dashboard with real-time machine status
```

## Data Model

### SensorCount Table

```sql
CREATE TABLE sensor_counts (
    id INTEGER PRIMARY KEY,
    machine_id INTEGER NOT NULL FOREIGN KEY,
    date DATE NOT NULL,
    daily_count INTEGER DEFAULT 0,
    total_count INTEGER DEFAULT 0,
    threshold_reached BOOLEAN DEFAULT FALSE,
    threshold_value INTEGER DEFAULT 300000,
    reset_by_user_id VARCHAR(100),
    reset_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sensor_machine_date ON sensor_counts(machine_id, date);
```

## Integration with Existing Systems

### 1. Machine Events
When impulse count reaches the threshold:
- A MachineEvent record is created with type: `preventive_maintenance_alert`
- This integrates with existing event tracking system

### 2. Preventive Maintenance Plans
Preventive maintenance execution reports now include:
- Current impulse count
- Percentage of threshold
- Trend analysis
- Days since last reset
- Impulses remaining until next alert

### 3. Dashboard KPIs
New metrics added:
- Machines with maintenance due
- Average impulse count across fleet
- Maintenance trend analysis

## Implementation Steps

### Step 1: Database Migration
```python
from app import create_app, db

app = create_app()
with app.app_context():
    # This creates the SensorCount table
    db.create_all()
```

### Step 2: Update Raspberry Pi Code
In your `monitor_buttons_and_downtime()` function, the impulse tracking is already implemented:

```python
# Record impulse on sensor trigger
if prev_sensor == GPIO.HIGH and curr_sensor == GPIO.LOW:
    with pending_count_lock:
        pending_sensor_count += 1

# Flush periodically
if time.time() - last_count_flush >= SENSOR_COUNT_FLUSH_INTERVAL:
    with pending_count_lock:
        to_send = pending_sensor_count
        pending_sensor_count = 0
    if to_send > 0:
        increment_sensor_count_async(to_send)
    last_count_flush = time.time()
```

### Step 3: Access the Dashboard
Navigate to: `http://your-app/api/sensor/dashboard`

### Step 4: View in Reports
When viewing preventive maintenance reports, sensor data is displayed automatically

## Usage Examples

### Python Backend

```python
from app.impulse_sensor import ImpulseDetector, SensorCountManager

# Create detector for a machine
detector = ImpulseDetector("machine_001", threshold=300000)

# Record impulse
detector.record_impulse()

# Check if should flush
if detector.should_flush():
    detector.flush_counts_async()

# Get status
status = detector.get_status()
print(f"Total: {status['total_count']}, Threshold reached: {status['threshold_reached']}")

# Reset counter after maintenance
detector.reset_counter(reset_by_user_id="tech_001")
```

### Manager Class

```python
from app.impulse_sensor import SensorCountManager

# Get 30-day statistics
stats = SensorCountManager.get_machine_sensor_stats(machine_id=1, days=30)
print(f"Daily average: {stats['daily_average']}")
print(f"Trend increase: {stats['trend_increase_percent']}%")

# Check if maintenance is due
is_due = SensorCountManager.is_maintenance_due(machine_id=1)
if is_due['maintenance_due']:
    print(f"Maintenance due: {is_due['reason']}")

# Get current status
status = SensorCountManager.get_threshold_status(machine_id=1)
print(f"Progress: {status['percentage']}%")
```

## Conditional Maintenance Rules

The system implements the following conditional rules:

### 1. Maintenance Status Determination
```python
if total_count >= 300000:
    status = "MAINTENANCE_DUE"
elif total_count >= 240000:  # 80%
    status = "WARNING"
else:
    status = "OK"
```

### 2. Automated Recommendations
- **Trend increase > 50%**: "Heavy usage detected. Monitor closely."
- **Daily average > 1000**: "Consider increasing maintenance frequency."
- **Days overdue > 5000 impulses**: "URGENT: Schedule immediately."

### 3. Reset Logic
Counter is reset to 0 after:
- Preventive maintenance completion confirmation
- User acknowledges maintenance performed
- System records who performed the reset and when

## Monitoring & Alerts

### Real-time Dashboard Features
1. **Machine Status Cards**
   - Current impulse count
   - Percentage of threshold
   - Maintenance status (OK/Warning/Due)
   - Last updated timestamp

2. **Alerts Section**
   - Highlighted alerts for machines requiring maintenance
   - Direct link to maintenance scheduling

3. **System Overview**
   - Total active machines
   - Machines in good condition
   - Machines at warning level
   - Machines with maintenance due

### Email Notifications
When threshold is reached:
- Email sent to machine supervisor
- Email sent to maintenance coordinator
- Includes machine name, current count, and recommended action

## Performance Considerations

1. **Buffering Strategy**
   - Impulses buffered in memory (pending_sensor_count)
   - Flushed to database every 5 seconds
   - Reduces database write operations

2. **Database Queries**
   - Indexed on (machine_id, date) for fast lookups
   - Aggregations cached in application layer
   - Statistics computed on-demand

3. **API Response Times**
   - Sensor count endpoint: < 100ms
   - Statistics endpoint: < 500ms
   - Dashboard: < 1000ms

## Troubleshooting

### Impulses Not Being Recorded
1. Check Raspberry Pi network connectivity
2. Verify API endpoint is accessible: `curl http://server:5000/api/sensor/status/machine_name`
3. Check logs for connection errors

### Threshold Not Triggering
1. Verify threshold value in database (should be 300,000)
2. Check SensorCount table has records
3. Confirm counter hasn't been reset unexpectedly

### Dashboard Not Loading
1. Ensure user is logged in
2. Check machines are marked as 'active' in database
3. Verify sensor_bp blueprint is registered in app

## Future Enhancements

1. **Machine Learning**
   - Predict maintenance needs based on usage patterns
   - Anomaly detection for unusual behavior

2. **Integration**
   - SMS alerts for critical maintenance
   - Third-party CMMS integration
   - IoT sensor integration

3. **Advanced Analytics**
   - Predictive maintenance scheduling
   - Spare parts usage correlation
   - Cost-benefit analysis

4. **Mobile App**
   - Mobile dashboard
   - Push notifications
   - Offline capability

## Support & Documentation

For detailed technical reference, see:
- `IMPULSE_DETECTION_GUIDE.md` - API Reference
- `app/impulse_sensor.py` - Source code with docstrings
- `app/routes/sensor_events.py` - Endpoint implementations

## Version History

**v1.0 - Initial Release**
- Core impulse detection system
- Threshold-based alerts
- Dashboard and reporting
- Database integration

---

**Created:** January 2024
**Status:** Production Ready

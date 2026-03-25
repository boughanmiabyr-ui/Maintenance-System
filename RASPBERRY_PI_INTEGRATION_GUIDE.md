# Raspberry Pi Machine Status Integration - Implementation Guide

## Overview

The Flask application now supports real-time machine status monitoring from Raspberry Pi controllers. The system tracks machine states, events, and provides a dashboard for operators and supervisors to monitor machine health.

## Architecture

### Components

1. **Database Models** (`app/models/__init__.py`)
   - `MachineStatus`: Real-time status tracker
   - `MachineEvent`: Event audit trail

2. **API Routes** (`app/routes/machine_events.py`)
   - Event endpoints for Raspberry Pi event submission
   - Status query endpoints for dashboard

3. **Frontend**
   - Machine Status Widget (`app/templates/machine_status_widget.html`)
   - Machine Status View (`app/templates/machine_status_view.html`)

4. **Routes** (`app/routes/main.py`)
   - `/machine-status` - Dashboard view for machine monitoring

## Database Schema

### MachineStatus Table
```
Columns:
- id (PK)
- machine_id (FK)
- machine_name (String)
- current_status (String: working, downtime, maintenance, break, offline)
- status_since (DateTime)
- last_event_type (String)
- last_user_start (String)
- last_user_end (String)
- cumulative_downtime_today (Float)
- current_downtime_duration (Integer - seconds)
- power_status (String)
- last_updated (DateTime)
```

### MachineEvent Table
```
Columns:
- id (PK)
- machine_id (FK)
- machine_name (String)
- event_type (String: downtime, maintenance, break, breakdown, power_cut, material_change)
- event_status (String: started, ended, cancelled)
- start_user_id (String)
- end_user_id (String)
- start_comment (Text)
- end_comment (Text)
- cancel_reason (Text)
- breakdown_type (String)
- event_start_time (DateTime)
- event_end_time (DateTime)
- duration_seconds (Integer)
- reaction_time_seconds (Integer)
- maintenance_arrival_time (DateTime)
- maintenance_arrival_user_id (String)
- created_at (DateTime)
- updated_at (DateTime)

Properties:
- duration_hours: Easy access in hours
- reaction_time_minutes: Easy access in minutes
```

## API Endpoints

### Reading Status

#### 1. Get Machine List
```
GET /api/events/machines/list
```
**Response:**
```json
{
  "machines": [
    {
      "id": 1,
      "machine_code": "M001",
      "machine_name": "Assembly Line 1",
      "department": "Production"
    }
  ]
}
```

#### 2. Get Current Machine Status
```
GET /api/events/machine_status/<machine_code>
```
**Response:**
```json
{
  "machine_name": "M001",
  "current_status": "working",
  "status_since": "2026-03-02T10:30:00",
  "power_status": "on",
  "last_event_type": "downtime",
  "last_user_start": "operator1",
  "last_user_end": "operator2",
  "cumulative_downtime_today": 2.5,
  "current_downtime_duration": 0,
  "last_updated": "2026-03-02T10:35:00"
}
```

#### 3. Get Recent Events
```
GET /api/events/recent/<machine_code>?hours=24
```
**Response:**
```json
{
  "events": [
    {
      "event_type": "downtime",
      "event_status": "ended",
      "event_start_time": "2026-03-02T09:00:00",
      "event_end_time": "2026-03-02T09:15:00",
      "duration_seconds": 900,
      "start_user_id": "operator1",
      "end_user_id": "operator2",
      "start_comment": "Machine jam",
      "end_comment": "Jam cleared"
    }
  ]
}
```

### Writing Events (from Raspberry Pi)

#### 1. Downtime Start
```
POST /api/events/downtime/<machine_code>
Content-Type: application/json

{
  "start_user_id": "operator1",
  "start_comment": "Machine stopped - jam detected"
}
```

#### 2. Downtime Reset (End)
```
POST /api/events/reset_downtime/<machine_code>
Content-Type: application/json

{
  "end_user_id": "operator1",
  "end_comment": "Issue resolved"
}
```

#### 3. Maintenance Start
```
POST /api/events/maintenance/<machine_code>
Content-Type: application/json

{
  "start_user_id": "operator1",
  "start_comment": "Preventive maintenance",
  "breakdown": "Preventive"
}
```

#### 4. Maintenance End
```
POST /api/events/reset_maintenance/<machine_code>
Content-Type: application/json

{
  "end_user_id": "technician1",
  "end_comment": "Maintenance complete"
}
```

#### 5. Maintenance Arrival (KPI Tracking)
```
POST /api/events/maintenance_arrival/<machine_code>
Content-Type: application/json

{
  "maintenance_arrival_user_id": "technician1",
  "reaction_time": 900
}
```

#### 6. Break Start
```
POST /api/events/break/<machine_code>
Content-Type: application/json

{
  "start_user_id": "operator1",
  "start_comment": "Lunch break"
}
```

#### 7. Break End
```
POST /api/events/reset_break/<machine_code>
Content-Type: application/json

{
  "end_user_id": "operator1",
  "end_comment": "Back to work"
}
```

#### 8. Power Cut
```
POST /api/events/power_cut/<machine_code>
Content-Type: application/json

{}
```

## Raspberry Pi Configuration

Your Raspberry Pi code should submit events to these endpoints. Example configuration:

```python
# Machine code (from database)
MACHINE_CODE = "M001"

# API Base URL
API_URL = "http://flask-app:5000"

# Event submission
import requests

def send_downtime_event(user_id, comment):
    url = f"{API_URL}/api/events/downtime/{MACHINE_CODE}"
    data = {
        "start_user_id": user_id,
        "start_comment": comment
    }
    requests.post(url, json=data)

def send_downtime_reset(user_id, comment):
    url = f"{API_URL}/api/events/reset_downtime/{MACHINE_CODE}"
    data = {
        "end_user_id": user_id,
        "end_comment": comment
    }
    requests.post(url, json=data)
```

## Dashboard Usage

### Accessing the Machine Status Dashboard

1. Navigate to: `/machine-status` in your application
2. Select a machine from the dropdown
3. View real-time status and recent events

### Status Colors
- **Green (Working)**: Machine is operating normally
- **Red (Downtime)**: Machine is stopped or experiencing issues
- **Yellow (Maintenance)**: Maintenance work is in progress
- **Blue (Break)**: Operator on break
- **Gray (Offline)**: Machine is powered off

### Information Displayed

1. **Current Status**: Color-coded status badge
2. **Duration**: How long the machine has been in current state
3. **User Information**: Last operator/technician involved
4. **Downtime Tracking**: 
   - Current downtime duration (for active downtime)
   - Cumulative downtime for the day
5. **Power Status**: On/Off indication
6. **Event History**: Last 50 events in past 24 hours

## Setting Up the Integration

### 1. Create Database Records

First, ensure your machines are in the database:

```python
from app.models import Machine, MachineStatus

# Create a machine
machine = Machine(
    machine_code='M001',
    machine_name='Assembly Line 1',
    department='Production',
    status='active'
)
db.session.add(machine)
db.session.commit()

# Create initial status record
status = MachineStatus(
    machine_id=machine.id,
    machine_name='M001',
    current_status='offline',
    power_status='off'
)
db.session.add(status)
db.session.commit()
```

### 2. Configure Raspberry Pi

Update your Raspberry Pi code to submit events to the Flask API.

### 3. Test the Integration

```bash
# Test downtime event
curl -X POST http://localhost:5000/api/events/downtime/M001 \
  -H "Content-Type: application/json" \
  -d '{"start_user_id": "op1", "start_comment": "Test"}'

# Check status
curl http://localhost:5000/api/events/machine_status/M001

# Get recent events
curl http://localhost:5000/api/events/recent/M001?hours=24
```

## Features

### Real-Time Status Tracking
- Automatic status updates from Raspberry Pi events
- Color-coded status display
- Current state duration tracking

### Event Auditing
- Complete event history with timestamps
- User accountability tracking
- Event comments and breakdown classification

### KPI Metrics
- **Reaction Time**: Time from breakdown detection to maintenance arrival
- **Downtime Tracking**: Daily cumulative downtime per machine
- **Event Duration**: Automatic calculation for each event

### Auto-Refresh
- Dashboard automatically refreshes every 30 seconds
- Manual refresh button available
- No page reload required

## Troubleshooting

### Events Not Appearing
1. Check that machine code matches database records
2. Verify API endpoints are accessible
3. Check application logs for errors
4. Ensure MachineStatus record exists for the machine

### Status Not Updating
1. Verify Raspberry Pi is sending events correctly
2. Check event endpoint responses for errors
3. Ensure database connection is active
4. Verify foreign key relationships are correct

### Dashboard Not Loading
1. Check that at least one machine exists in database
2. Verify user has appropriate role (admin, supervisor, technician)
3. Check browser developer console for JavaScript errors
4. Verify API endpoints are responding

## Permissions

Access to machine status monitoring is granted to users with these roles:
- `admin`
- `supervisor`
- `technician`

## Next Steps

1. Configure your Raspberry Pi to send events to the Flask API
2. Test with sample events using curl or Postman
3. Monitor the dashboard for events appearing correctly
4. Set up alerts/notifications for critical downtime (future enhancement)

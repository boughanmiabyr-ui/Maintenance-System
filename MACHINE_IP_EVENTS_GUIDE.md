# Machine IP Address & Events - Complete Reference

## 📍 WHERE THE IP ADDRESS WAS ADDED

### 1. Database Model (ORM - SQLAlchemy)
**File**: `app/models/__init__.py` - Lines 182-207

```python
class Machine(db.Model):
    __tablename__ = 'machines'
    
    id = db.Column(db.Integer, primary_key=True)
    machine_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    machine_name = db.Column(db.String(200), nullable=True)          # ← NEW
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(200))
    department = db.Column(db.String(100), index=True)
    zone = db.Column(db.String(100), nullable=True, index=True)      # ← NEW
    zone_id = db.Column(db.Integer, db.ForeignKey('zones.id'), nullable=True)  # ← NEW
    ip_address = db.Column(db.String(50), unique=True, nullable=True, index=True)  # ← NEW
    model = db.Column(db.String(100))
    manufacturer = db.Column(db.String(100))
    purchase_date = db.Column(db.Date)
    installation_date = db.Column(db.Date)
    status = db.Column(db.String(50), default='active', index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### 2. SQL Migration Script
**File**: `migration_add_machine_ip.sql`

This file contains the SQL commands to add the new columns to your database.

---

## 🔍 HOW TO QUERY THE LATEST EVENTS

### Option 1: Quick Command Line Tool
**File**: `check_events_quick.py`

```bash
# Show all machines with latest event
python check_events_quick.py

# Show events for specific machine M001 (last 24 hours)
python check_events_quick.py M001

# Show events from last 12 hours
python check_events_quick.py M001 12

# Show all currently active events
python check_events_quick.py --active

# Show all machines
python check_events_quick.py --all
```

**Example Output**:
```
Machine: M001
  Name: Assembly Line 1
  IP: 10.110.30.15
  Department: Production
  Zone: Zone A
  Latest Event: downtime (ended)
    Time: 2026-03-16 15:30:22
  Status: working | Downtime: 2.50h
```

### Option 2: Interactive Query Tool
**File**: `query_machine_events.py`

```bash
python query_machine_events.py
```

This gives you an interactive menu:
```
Available options:
  1. Get machine information & IP addresses
  2. Get latest events (all machines)
  3. Get latest events for specific machine
  4. Get currently active events
  5. Get downtime summary
  6. Exit
```

### Option 3: Programmatic Access (Python)

```python
from app.models import Machine, MachineEvent, MachineStatus
from app import create_app
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    # Get a machine
    machine = Machine.query.filter_by(machine_code='M001').first()
    
    # Get its IP address
    print(f"Machine IP: {machine.ip_address}")
    
    # Get latest event
    latest_event = MachineEvent.query.filter_by(
        machine_id=machine.id
    ).order_by(MachineEvent.event_start_time.desc()).first()
    
    print(f"Latest Event: {latest_event.event_type}")
    print(f"Status: {latest_event.event_status}")
    print(f"Started: {latest_event.event_start_time}")
    
    # Get all events from last 24 hours
    since = datetime.utcnow() - timedelta(hours=24)
    events = MachineEvent.query.filter(
        MachineEvent.machine_id == machine.id,
        MachineEvent.event_start_time >= since
    ).order_by(MachineEvent.event_start_time.desc()).all()
    
    for event in events:
        print(f"- {event.event_type}: {event.event_status}")
    
    # Get current status
    status = MachineStatus.query.filter_by(machine_id=machine.id).first()
    print(f"Current Status: {status.current_status}")
    print(f"Cumulative Downtime Today: {status.cumulative_downtime_today:.2f} hours")
```

### Option 4: API Endpoints

**Get Machine Name from IP** (for Raspberry Pi initialization):
```bash
curl -X POST http://localhost:5000/api/events/get_machine_name \
  -H "Content-Type: application/json" \
  -d '{"ip_address": "10.110.30.15"}'

Response:
{
  "machine_name": "M001",
  "machine_id": 1,
  "department": "Production",
  "zone": "Zone A"
}
```

**Get Recent Events** (last 24 hours):
```bash
curl http://localhost:5000/api/events/recent/M001?hours=24

Response:
{
  "events": [
    {
      "event_type": "downtime",
      "event_status": "ended",
      "event_start_time": "2026-03-16T15:00:00",
      "event_end_time": "2026-03-16T15:30:00",
      "duration_seconds": 1800,
      "start_user_id": "operator1",
      "end_user_id": "operator2",
      "start_comment": "Machine jam"
    }
  ]
}
```

---

## 📊 MACHINE EVENTS DATABASE SCHEMA

### MachineEvent Table
```
id                              INTEGER (primary key)
machine_id                      INTEGER (foreign key) - Links to Machine
machine_name                    STRING - Machine code
event_type                      STRING - downtime, maintenance, break, breakdown, power_cut, material_change
event_status                    STRING - started, ended, cancelled
start_user_id                   STRING - Operator/technician who started
end_user_id                     STRING - Operator/technician who ended
start_comment                   TEXT - Reason/details for start
end_comment                     TEXT - Reason/details for end
cancel_reason                   TEXT - Why was it cancelled
breakdown_type                  STRING - Curative/Corrective/Preventive (for maintenance)
event_start_time                DATETIME - When event started
event_end_time                  DATETIME - When event ended
duration_seconds                INTEGER - Total duration
reaction_time_seconds           INTEGER - Time to maintenance arrival (KPI)
maintenance_arrival_time        DATETIME - When technician arrived
maintenance_arrival_user_id     STRING - Which technician arrived
created_at                      DATETIME
updated_at                      DATETIME
```

### MachineStatus Table
```
id                              INTEGER (primary key)
machine_id                      INTEGER (foreign key)
machine_name                    STRING
current_status                  STRING - working, downtime, maintenance, break, offline
status_since                    DATETIME - When current status started
last_event_type                 STRING - Type of last event
last_user_start                 STRING - Last operator who started an event
last_user_end                   STRING - Last operator who ended an event
cumulative_downtime_today       FLOAT - Total downtime hours for the day
current_downtime_duration       INTEGER - Seconds for ongoing downtime
power_status                    STRING - on/off
last_updated                    DATETIME
```

---

## 🚀 QUICK START: UPDATE YOUR DATABASE

### Step 1: Run Migration
```bash
# Using SQLite (if that's what you're using)
sqlite3 your_database.db < migration_add_machine_ip.sql

# Or for PostgreSQL
psql -U username -d database_name -f migration_add_machine_ip.sql
```

### Step 2: Add IP Addresses to Machines
```bash
# Interactive mode
python check_events_quick.py
```

Or manually update:
```python
from app.models import Machine
from app import create_app, db

app = create_app()

with app.app_context():
    # Update machine M001
    machine = Machine.query.filter_by(machine_code='M001').first()
    machine.ip_address = '10.110.30.15'
    machine.machine_name = 'Assembly Line 1'
    machine.zone = 'Production Zone A'
    db.session.commit()
    print(f"Updated {machine.machine_code} with IP {machine.ip_address}")
```

### Step 3: Verify Setup
```bash
python check_events_quick.py --all
```

Expected output:
```
Machine: M001
  Name: Assembly Line 1
  IP: 10.110.30.15 ✓
  Department: Production
  Zone: Production Zone A
  Latest Event: No events yet
  Status: offline | Downtime: 0.00h
```

---

## 📡 RASPBERRY PI INTEGRATION

### Raspberry Pi Initialization
```python
# In raspberrycode.py, the code does this:
ip_address = get_ip_address()  # Get Pi's IP
machine_name = fetch_machine_name(ip_address)  # Query API

# This calls:
# POST /api/events/get_machine_name
# {
#   "ip_address": "10.110.30.15"
# }
```

### What Happens Next
1. Raspberry Pi gets its machine code (e.g., "M001")
2. Pi starts sending events to: `/api/events/downtime/M001`
3. Events are saved to `machine_events` table
4. Status is updated in `machine_status` table
5. You can query it anytime using the tools above

---

## 🔧 TROUBLESHOOTING

### Machine IP Not Set
```bash
# Check which machines don't have IP
python -c "
from app.models import Machine
from app import create_app

app = create_app()
with app.app_context():
    machines = Machine.query.filter(Machine.ip_address == None).all()
    for m in machines:
        print(f'{m.machine_code}: NO IP ADDRESS')
"
```

### No Events Recorded
```bash
# Check if events table is empty
python -c "
from app.models import MachineEvent
from app import create_app

app = create_app()
with app.app_context():
    count = MachineEvent.query.count()
    print(f'Total events: {count}')
"
```

### Verify IP Address Works
```bash
# Test API endpoint directly
curl -X POST http://localhost:5000/api/events/get_machine_name \
  -H "Content-Type: application/json" \
  -d '{"ip_address": "10.110.30.15"}'

# Should return machine info, not 404
```

---

## 📁 FILES REFERENCE

| File | Purpose |
|------|---------|
| `app/models/__init__.py` | Machine model with IP field (lines 182-207) |
| `app/routes/machine_events.py` | API endpoints including `/api/events/get_machine_name` |
| `migration_add_machine_ip.sql` | SQL script to add columns to database |
| `check_events_quick.py` | Quick command-line tool to check events |
| `query_machine_events.py` | Interactive event query tool |
| `RASPBERRY_PI_INTEGRATION_GUIDE.md` | Full API documentation |

---

## 💡 SUMMARY

✅ **IP Address Field**: Added to Machine model (`ip_address` column)
✅ **Zone Field**: Added for organization (`zone` column)
✅ **API Endpoint**: `/api/events/get_machine_name` - Raspberry Pi uses this
✅ **Event Tracking**: All events stored in `machine_events` table
✅ **Query Tools**: Two tools to query events from command line
✅ **Status Tracking**: `machine_status` tracks current state

**To see latest events from a machine**:
```bash
python check_events_quick.py M001
```

That's it! 🎉

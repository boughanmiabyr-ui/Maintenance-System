# ✅ Flask App Components - Verification Checklist

This document shows what components are required for Raspberry Pi integration to work.

---

## 📦 Required Flask Components

### ✅ 1. Models (app/models/__init__.py)

**Status**: ✅ PRESENT

**Required Models**:
- ✅ `Machine` - With fields: `ip_address`, `machine_code`, `machine_name`, `zone`
- ✅ `MachineStatus` - Tracks current status with fields: `current_status`, `status_since`, `cumulative_downtime_today`
- ✅ `MachineEvent` - Event records with: `event_type`, `event_status`, `start_user_id`, `end_user_id`, `event_start_time`, `event_end_time`

**How to verify**:
```python
from app.models import Machine, MachineStatus, MachineEvent
print("✓ All models imported successfully")
```

---

### ✅ 2. API Routes (app/routes/machine_events.py)

**Status**: ✅ PRESENT

**Required Endpoints**:
- ✅ `POST /api/events/get_machine_name` - CRITICAL (Raspberry Pi uses this to identify)
- ✅ `GET /api/events/machines/list` - List all machines
- ✅ `GET /api/events/recent/<machine_name>` - Get event history
- ✅ `POST /api/events/downtime/<machine_name>` - Start downtime
- ✅ `POST /api/events/reset_downtime/<machine_name>` - End downtime
- ✅ `POST /api/events/maintenance/<machine_name>` - Start maintenance
- ✅ `POST /api/events/reset_maintenance/<machine_name>` - End maintenance
- ✅ `POST /api/events/break/<machine_name>` - Start break
- ✅ `POST /api/events/reset_break/<machine_name>` - End break
- ✅ `POST /api/events/power_cut/<machine_name>` - Record power cut

**How to verify**:
```bash
# Test the critical endpoint
curl -X POST http://localhost:5000/api/events/get_machine_name \
  -H "Content-Type: application/json" \
  -d '{"ip_address": "10.110.30.15"}'

# Should return:
# {"machine_name": "M001", "machine_id": 1, "department": "...", "zone": "..."}
```

---

### ✅ 3. Blueprint Registration (app/__init__.py)

**Status**: ✅ PRESENT

**Required Code**:
```python
# Line ~47
from app.routes.machine_events import events_bp

# Line ~60
app.register_blueprint(events_bp)
```

**How to verify**:
```bash
python main.py

# In output, should see:
# * Running on http://127.0.0.1:5000
# No error messages about events_bp
```

---

### ✅ 4. Database Tables

**Status**: ⚠️ NEEDS VERIFICATION

**Required Tables** (with sample data):

#### machines table
```
CREATE TABLE machines (
  id INT PRIMARY KEY AUTO_INCREMENT,
  machine_code VARCHAR(100),
  machine_name VARCHAR(100),
  ip_address VARCHAR(45) UNIQUE,
  zone VARCHAR(100),
  department VARCHAR(100),
  status VARCHAR(50),
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

-- Sample row:
INSERT INTO machines VALUES (
  1, 'M001', 'Machine 1', '10.110.30.15', 'Zone A', 'Production', 'active', NOW(), NOW()
);
```

#### machine_events table
```
CREATE TABLE machine_events (
  id INT PRIMARY KEY AUTO_INCREMENT,
  machine_id INT,
  event_type VARCHAR(100),
  event_status VARCHAR(50),
  event_start_time DATETIME,
  event_end_time DATETIME,
  start_user_id INT,
  end_user_id INT,
  start_comment TEXT,
  end_comment TEXT,
  FOREIGN KEY (machine_id) REFERENCES machines(id)
);
```

**How to verify**:
```sql
USE maintenance_system_v2;

-- Check tables exist
SHOW TABLES LIKE 'machine%';

-- Check machines table structure
DESCRIBE machines;

-- Check if machines have IPs
SELECT machine_code, ip_address FROM machines;
```

---

## 🧪 Complete System Test

Run this to verify EVERYTHING is working:

```bash
# 1. Start Flask
python main.py &

# Wait 3 seconds
sleep 3

# 2. Test API is responding
curl http://localhost:5000/api/events/machines/list

# 3. From another terminal, test with a real machine IP
curl -X POST http://localhost:5000/api/events/get_machine_name \
  -H "Content-Type: application/json" \
  -d '{"ip_address": "10.110.30.15"}'

# Should return: {"machine_name": "M001", ...}
```

---

## ⚠️ Common Issues

### Issue 1: "ModuleNotFoundError: No module named 'app.routes.machine_events'"
**Solution**: Check if file `app/routes/machine_events.py` exists
```bash
ls -la app/routes/machine_events.py
```

### Issue 2: "404 Not Found" when calling /api/events/*
**Solution**: Blueprint may not be registered. Check app/__init__.py has:
```python
from app.routes.machine_events import events_bp
app.register_blueprint(events_bp)
```

### Issue 3: Machine not found for IP (404)
**Solution**: Machine IP not in database. Add it:
```sql
UPDATE machines SET ip_address='10.110.30.15' WHERE machine_code='M001';
```

### Issue 4: Missing machine_events table
**Solution**: Database migration not applied. Run:
```bash
python
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
```

---

## 📊 Verification Commands

### Check Flask starts without errors:
```bash
python main.py
# Should show: * Running on http://127.0.0.1:5000
# No error messages
```

### Check API responds:
```bash
curl http://localhost:5000/api/events/machines/list
# Should return: {"machines": [...]}
```

### Check database has machines:
```sql
SELECT COUNT(*) as total_machines FROM machines;
SELECT COUNT(*) as machines_with_ip FROM machines WHERE ip_address IS NOT NULL;
```

### Check machine events table exists and is empty:
```sql
SELECT COUNT(*) as total_events FROM machine_events;
# Returns: 0 (initially)
```

---

## ✅ Pre-Launch Checklist

Before running Raspberry Pi, confirm:

- [ ] `app/routes/machine_events.py` exists
- [ ] `app/__init__.py` imports and registers `events_bp`
- [ ] Models include `MachineStatus` and `MachineEvent`
- [ ] Database has `machines` table with NUL-NULL `ip_address` column
- [ ] Database has `machine_events` table
- [ ] At least one machine exists with an IP address assigned
- [ ] Flask starts without errors: `python main.py`
- [ ] API endpoint responds: `curl http://localhost:5000/api/events/machines/list`
- [ ] Machine name endpoint works:
  ```bash
  curl -X POST http://localhost:5000/api/events/get_machine_name \
    -H "Content-Type: application/json" \
    -d '{"ip_address": "YOUR_MACHINE_IP"}'
  # Returns: {"machine_name": "M001", ...}
  ```
- [ ] MAIN_API_BASE_URL updated in raspberrycode.py
- [ ] Raspberry Pi can reach Flask server: `ping FLASK_SERVER_IP`

---

## 🚀 If All Checks Pass

Your Flask app is ready for Raspberry Pi integration:

1. Run Flask: `python main.py`
2. Run Raspberry Pi code: `python raspberrycode.py`
3. Events should appear in database
4. Dashboard should show real-time status

---

## 📝 File Locations Summary

| Component | File | Status |
|-----------|------|--------|
| API Routes | `app/routes/machine_events.py` | ✅ Present |
| Models | `app/models/__init__.py` | ✅ Present |
| Blueprint Registration | `app/__init__.py` | ✅ Present |
| Database Schema | No file (created at runtime or via SQL) | ⚠️ Check with SQL |
| Sample Data | No file (add manually) | ⚠️ Add machines with IPs |


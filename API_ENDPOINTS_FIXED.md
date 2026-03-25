# ✅ Raspberry Pi API Endpoints - FIXED

## What Was Wrong

Raspberry Pi code was calling the wrong API endpoint paths:

| Issue | Before | After |
|-------|--------|-------|
| **Base URL** | `http://10.110.30.15:1250/api` | `http://192.168.137.1:5000/api` ✓ |
| **Machine Name Endpoint** | `/api/get_machine_name` | `/api/events/get_machine_name` ✓ |
| **Event Endpoints** | `/api/downtime/M001` | `/api/events/downtime/M001` ✓ |

---

## ✅ Changes Made

### ✓ Change 1: Base URL (Line 44)
Updated to use your laptop IP and Flask port 5000
```python
# Before:
MAIN_API_BASE_URL = "http://10.110.30.15:1250/api"

# After:
MAIN_API_BASE_URL = "http://192.168.137.1:5000/api"
```

### ✓ Change 2: Get Machine Name Endpoint (Line 113)
Added missing `/events` in the path
```python
# Before:
url = f"{MAIN_API_BASE_URL}/get_machine_name"

# After:
url = f"{MAIN_API_BASE_URL}/events/get_machine_name"
```

### ✓ Change 3: Event Endpoints (Line 180)
Added missing `/events` in all event paths
```python
# Before:
url = f"{MAIN_API_BASE_URL}/{event_type}/{TEAM_NAME}"

# After:
url = f"{MAIN_API_BASE_URL}/events/{event_type}/{TEAM_NAME}"
```

---

## 🧪 Now Test It

### Step 1: Start Flask (on your laptop)
```bash
cd c:\Users\Arij Arouja\Desktop\appstage2026PFE-main
python main.py

# Should see:
# * Running on http://127.0.0.1:5000
```

### Step 2: Update Database (Machine IP)
```sql
-- Login to MySQL
mysql -u root -p

-- Update your database
USE maintenance_system_v2;
UPDATE machines SET ip_address='192.168.137.102' WHERE machine_code='M001';

-- Verify
SELECT machine_code, ip_address FROM machines;
```

### Step 3: Test API Endpoint
```bash
# From your laptop or Raspberry Pi
curl -X POST http://192.168.137.1:5000/api/events/get_machine_name \
  -H "Content-Type: application/json" \
  -d '{"ip_address": "192.168.137.102"}'

# Should return:
# {"machine_name": "M001", "machine_id": 1, "department": "...", "zone": "..."}
```

**If you get JSON back** ✓ - API is working!  
**If you get 404** ❌ - Flask might not be running or route not registered

### Step 4: Run Raspberry Pi Code
```bash
# On Raspberry Pi
python raspberrycode.py

# Should show:
# System started for M001. Waiting for sensor triggers...
# NOT: System started for Unknown
```

### Step 5: Check Flask Logs
Look in the Flask terminal, you should see:
```
192.168.137.102 - - [16/Mar/2026 12:35:14] "POST /api/events/get_machine_name HTTP/1.1" 200 -
INFO:app.models:Machine found for IP 192.168.137.102: M001
```

**If you see 200** ✓ - API call succeeded!  
**If you see 404** ❌ - Endpoint path still wrong  
**If you see 500** ❌ - Server error (check Flask console)

---

## 📊 All Correct Endpoint Paths

These are ALL the endpoints your Raspberry Pi might call:

```
✓ POST   /api/events/get_machine_name
✓ GET    /api/events/machines/list
✓ GET    /api/events/machine_status/<machine_name>
✓ POST   /api/events/downtime/<machine_name>
✓ POST   /api/events/reset_downtime/<machine_name>
✓ POST   /api/events/maintenance/<machine_name>
✓ POST   /api/events/reset_maintenance/<machine_name>
✓ POST   /api/events/maintenance_arrival/<machine_name>
✓ POST   /api/events/break/<machine_name>
✓ POST   /api/events/reset_break/<machine_name>
✓ POST   /api/events/power_cut/<machine_name>
```

All have `/api/events/` prefix - this is critical!

---

## 🆘 If Still Getting 404

Check these in order:

1. **Flask is running**
   ```bash
   ps aux | grep main.py
   # Or: tasklist | findstr python
   ```

2. **machine_events.py file exists**
   ```bash
   ls app/routes/machine_events.py
   # Should exist
   ```

3. **Blueprint is registered in app/__init__.py**
   ```bash
   grep "events_bp" app/__init__.py
   # Should show import and register lines
   ```

4. **URL has /events in it**
   ```python
   # Should be:
   http://192.168.137.1:5000/api/events/get_machine_name
   # NOT:
   http://192.168.137.1:5000/api/get_machine_name
   ```

5. **Flask app is starting without errors**
   - Look at Flask terminal output for any import errors or registration failures

---

## 📋 Verification Checklist

- [ ] raspberrycode.py line 44 updated to `192.168.137.1:5000`
- [ ] raspberrycode.py line 113 has `/events/get_machine_name`
- [ ] raspberrycode.py line 180 has `/events/{event_type}`
- [ ] Flask is running: `python main.py`
- [ ] Machine IP in database: `192.168.137.102`
- [ ] API endpoint test returns 200 with JSON
- [ ] Raspberry Pi code shows "System started for M001" (not Unknown)
- [ ] Flask logs show successful POST requests (200 status)

---

## 🚀 Expected Flow After Fix

1. **Raspberry Pi starts** → Calls `/api/events/get_machine_name` with its IP
2. **Flask responds** → 200 OK with machine code "M001"
3. **Raspberry Pi receives** → Machine code and sets TEAM_NAME = "M001"
4. **Raspberry Pi displays** → "System started for M001"
5. **When event triggered** → Sends to `/api/events/downtime/M001`
6. **Flask records** → Event saved to database
7. **Dashboard shows** → Real-time status update

---

## 💡 Summary

**Fixed**: ✓ All 3 API endpoint issues  
**Updated**: ✓ Base URL to correct laptop IP and port  
**Ready to test**: ✓ Run Flask → Test API → Run Raspberry Pi

**Next Step**: Run `python main.py` and test the API endpoint above!

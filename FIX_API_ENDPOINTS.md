# 🚨 Raspberry Pi API Endpoints - 404 Error Fix

## Current Issue

```
Error: "POST /api/get_machine_name HTTP/1.1" 404
```

**Root Cause**: Raspberry Pi code is calling the WRONG endpoint paths.

---

## 🎯 The Problem Explained

### Flask Defines Routes Like This:

```python
# In app/routes/machine_events.py
events_bp = Blueprint('events', __name__, url_prefix='/api/events')

@events_bp.route('/get_machine_name', methods=['POST'])
def get_machine_name():
    # Route: /api/events/get_machine_name ✓ CORRECT
```

The full path is: **`/api/events/get_machine_name`**

### But Raspberry Pi Calls:

```python
# In raspberrycode.py line 44
MAIN_API_BASE_URL = "http://10.110.30.15:1250/api"

# Line 113
url = f"{MAIN_API_BASE_URL}/get_machine_name"
# Results in: /api/get_machine_name ❌ WRONG (missing /events)
```

### Issue 1: Wrong Base URL
```python
MAIN_API_BASE_URL = "http://10.110.30.15:1250/api"
# ❌ WRONG - old IP (10.110.30.15), wrong port (1250)
# Should be your laptop IP on new connection
```

### Issue 2: Missing `/events` in Endpoint Paths
```python
url = f"{MAIN_API_BASE_URL}/get_machine_name"
# ❌ WRONG: /api/get_machine_name
# ✓ CORRECT: /api/events/get_machine_name

url = f"{MAIN_API_BASE_URL}/{event_type}/{TEAM_NAME}"
# ❌ WRONG: /api/downtime/M001
# ✓ CORRECT: /api/events/downtime/M001
```

---

## ✅ All Flask API Endpoints (Correct Paths)

These are ALL the endpoints Raspberry Pi might need:

```
POST   /api/events/get_machine_name          ← Get machine code from IP
GET    /api/events/machines/list             ← List all machines
GET    /api/events/recent/<machine_name>     ← Get recent events
GET    /api/events/machine_status/<name>     ← Get current status
POST   /api/events/downtime/<machine_name>   ← Start downtime
POST   /api/events/reset_downtime/<name>     ← End downtime
POST   /api/events/maintenance/<machine_name> ← Start maintenance
POST   /api/events/reset_maintenance/<name>   ← End maintenance
POST   /api/events/maintenance_arrival/<name> ← Maintenance arrival
POST   /api/events/break/<machine_name>       ← Start break
POST   /api/events/reset_break/<name>        ← End break
POST   /api/events/power_cut/<machine_name>   ← Power cut event
```

**Key Point**: ALL endpoints start with `/api/events/` - the `/events` is CRITICAL

---

## 🔧 How to Fix raspberrycode.py

### Fix 1: Update Base URL (Line 44)

**Current** (WRONG):
```python
MAIN_API_BASE_URL = "http://10.110.30.15:1250/api"
```

**Change To** (CORRECT):
```python
# Replace with your laptop's IP on the new connection
# Example: if your laptop is 10.0.0.5
MAIN_API_BASE_URL = "http://10.0.0.5:5000/api"

# Or more precisely for your case:
MAIN_API_BASE_URL = "http://192.168.x.x:5000/api"  # Use your actual laptop IP
```

**Get your laptop IP**:
```powershell
ipconfig | findstr /i "IPv4"
# Look for your current connection (not the old 10.110.30.15)
```

### Fix 2: Update Machine Name Endpoint (Line 113)

**Current** (WRONG):
```python
url = f"{MAIN_API_BASE_URL}/get_machine_name"
# Results in: http://.../api/get_machine_name ❌
```

**Change To** (CORRECT):
```python
url = f"{MAIN_API_BASE_URL}/events/get_machine_name"
# Results in: http://.../api/events/get_machine_name ✓
```

### Fix 3: Update Event Endpoints (Line 180)

**Current** (WRONG):
```python
url = f"{MAIN_API_BASE_URL}/{event_type}/{TEAM_NAME}"
# Results in: http://.../api/downtime/M001 ❌
```

**Change To** (CORRECT):
```python
url = f"{MAIN_API_BASE_URL}/events/{event_type}/{TEAM_NAME}"
# Results in: http://.../api/events/downtime/M001 ✓
```

---

## 📝 Complete Fixed Sections

### Section 1: Line 44 - Update Base URL

**Before**:
```python
# Main Flask app API base URL
MAIN_API_BASE_URL = "http://10.110.30.15:1250/api"
```

**After**:
```python
# Main Flask app API base URL - UPDATE THIS TO YOUR LAPTOP IP
# Example: http://192.168.1.100:5000/api
MAIN_API_BASE_URL = "http://192.168.137.1:5000/api"  # Change to your laptop IP
```

---

### Section 2: Lines 110-120 - fetch_machine_name function

**Before**:
```python
def fetch_machine_name(ip_address):
    try:
        url = f"{MAIN_API_BASE_URL}/get_machine_name"
        data = {"ip_address": ip_address}
        response = requests.post(url, json=data, timeout=5)
        if response.status_code == 200:
            machine_name = response.json().get("machine_name")
            logger.info(f"Retrieved machine name: {machine_name} for IP: {ip_address}")
            return machine_name
```

**After**:
```python
def fetch_machine_name(ip_address):
    try:
        url = f"{MAIN_API_BASE_URL}/events/get_machine_name"  # Added /events
        data = {"ip_address": ip_address}
        response = requests.post(url, json=data, timeout=5)
        if response.status_code == 200:
            machine_name = response.json().get("machine_name")
            logger.info(f"Retrieved machine name: {machine_name} for IP: {ip_address}")
            return machine_name
```

---

### Section 3: Lines 170-210 - send_event_async function

**Before**:
```python
def send_event_async(event_type, duration=None, start_user_id=None, end_user_id=None, start_comment=None, end_comment=None, cancel_reason=None, reaction_time=None, maintenance_arrival_user_id=None, breakdown=None):
    if TEAM_NAME is None:
        logger.error("Cannot send event: TEAM_NAME not set")
        display_lcd_message("Error: TEAM_NAME\nnot set")
        return
    
    def send_request():
        try:
            url = f"{MAIN_API_BASE_URL}/{event_type}/{TEAM_NAME}"
            data = {
```

**After**:
```python
def send_event_async(event_type, duration=None, start_user_id=None, end_user_id=None, start_comment=None, end_comment=None, cancel_reason=None, reaction_time=None, maintenance_arrival_user_id=None, breakdown=None):
    if TEAM_NAME is None:
        logger.error("Cannot send event: TEAM_NAME not set")
        display_lcd_message("Error: TEAM_NAME\nnot set")
        return
    
    def send_request():
        try:
            url = f"{MAIN_API_BASE_URL}/events/{event_type}/{TEAM_NAME}"  # Added /events
            data = {
```

---

## 🧪 Testing Each Endpoint

After making the fixes, test each endpoint:

### Test 1: Get Machine Name
```bash
curl -X POST http://192.168.137.1:5000/api/events/get_machine_name \
  -H "Content-Type: application/json" \
  -d '{"ip_address": "192.168.137.102"}'

# Should return:
# {"machine_name": "M001", "machine_id": 1, ...}
```

### Test 2: List Machines
```bash
curl http://192.168.137.1:5000/api/events/machines/list

# Should return:
# {"machines": [...]}
```

### Test 3: Get Machine Status
```bash
curl http://192.168.137.1:5000/api/events/machine_status/M001

# Should return machine status data
```

### Test 4: Send Downtime Event
```bash
curl -X POST http://192.168.137.1:5000/api/events/downtime/M001 \
  -H "Content-Type: application/json" \
  -d '{"start_user_id": "1", "start_comment": "Test"}'

# Should return 201 Created
```

---

## 📋 Complete Fix Checklist

- [ ] **Line 44**: Update `MAIN_API_BASE_URL` to your laptop's current IP and port 5000
- [ ] **Line 113**: Change `/get_machine_name` to `/events/get_machine_name`
- [ ] **Line 180**: Change `/{event_type}/` to `/events/{event_type}/`
- [ ] Test endpoint: `curl http://YOUR_IP:5000/api/events/get_machine_name`
- [ ] Verify Flask is running: `python main.py`
- [ ] Verify machine IP in database: `SELECT ip_address FROM machines`
- [ ] Run Raspberry Pi code: `python raspberrycode.py`
- [ ] Check Flask logs for successful POST requests
- [ ] Verify "System started for M001" (not "Unknown")

---

## 🚀 Your IP Information

**Current Setup** (from your connection):
- Raspberry Pi: `192.168.137.102`
- Laptop: `192.168.137.x` (need to find this)
- Flask Port: `5000`

**To find your laptop IP**:
```powershell
# On laptop
ipconfig | findstr /i "IPv4"

# Look for the one on the same network as 192.168.137.102
# Probably 192.168.137.1 or similar
```

**Then update line 44**:
```python
MAIN_API_BASE_URL = "http://192.168.137.1:5000/api"  # Your actual IP
```

---

## 📱 Expected Logs After Fix

**In Flask terminal** (when Raspberry Pi connects):
```
192.168.137.102 - - [16/Mar/2026 12:30:14] "POST /api/events/get_machine_name HTTP/1.1" 200 -
INFO:app.models:Machine found for IP 192.168.137.102: M001
202.168.137.102 - - [16/Mar/2026 12:30:15] "POST /api/events/downtime/M001 HTTP/1.1" 201 -
```

**In Raspberry Pi terminal**:
```
System started for M001. Waiting for sensor triggers...
[sensor trigger]
Downtime alert triggered
Event downtime started
Downtime Started
```

If you still see **404** after fixing, double-check:
1. Flask is running: `python main.py`
2. URL has `/events` in path
3. Endpoint path is `/api/events/...` not `/api/...`

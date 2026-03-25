# Raspberry Pi Code - What Needs to Change

## 🎯 The Issue: "Machine Unknown"

This means one of these is wrong:
1. **Raspberry Pi can't reach Flask API** (network issue)
2. **IP address not in database** (database issue)
3. **Raspberry Pi sending wrong IP** (code issue)
4. **API endpoint not working** (Flask issue)

---

## 🔧 Changes Needed in raspberrycode.py

### CHANGE 1: Update Base URL (Line 44) ✅ REQUIRED

**Current:**
```python
MAIN_API_BASE_URL = "http://10.110.30.15:1250/api"
```

**Change To** (your Flask server URL):
```python
# If Flask is at 192.168.1.100 port 5000
MAIN_API_BASE_URL = "http://192.168.1.100:5000/api"

# If Flask is at 10.110.30.50 port 5000
MAIN_API_BASE_URL = "http://10.110.30.50:5000/api"
```

---

### CHANGE 2: Add Error Logging in fetch_machine_name (OPTIONAL but HELPFUL)

**Find this function** (around line 113):
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
        else:
            logger.warning(f"Failed to fetch machine name: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error fetching machine name from {url}: {e}")
        return None
```

**Add More Debugging:**
```python
def fetch_machine_name(ip_address):
    try:
        url = f"{MAIN_API_BASE_URL}/get_machine_name"
        data = {"ip_address": ip_address}
        
        print(f"DEBUG: Attempting to reach: {url}")  # ← ADD THIS
        print(f"DEBUG: Sending IP: {ip_address}")   # ← ADD THIS
        
        response = requests.post(url, json=data, timeout=5)
        
        print(f"DEBUG: Response status: {response.status_code}")  # ← ADD THIS
        print(f"DEBUG: Response body: {response.text}")           # ← ADD THIS
        
        if response.status_code == 200:
            machine_name = response.json().get("machine_name")
            logger.info(f"Retrieved machine name: {machine_name} for IP: {ip_address}")
            print(f"SUCCESS: Got machine name: {machine_name}")    # ← ADD THIS
            return machine_name
        else:
            logger.warning(f"Failed to fetch machine name: {response.status_code} - {response.text}")
            print(f"ERROR: Server returned {response.status_code}")  # ← ADD THIS
            return None
    except Exception as e:
        logger.error(f"Error fetching machine name from {url}: {e}")
        print(f"ERROR: Connection failed - {e}")                  # ← ADD THIS
        return None
```

This will show you exactly what's happening when it tries to get the machine name.

---

### CHANGE 3: Handle "None" Machine Name (IMPORTANT)

Look for the code that uses `TEAM_NAME` and add safety checks:

**Find** (around line 280 in main()):
```python
TEAM_NAME = fetch_machine_name(ip_address)
if not TEAM_NAME:
    logger.error("Failed to retrieve machine name. Using default 'Unknown'")
    TEAM_NAME = "Unknown"
```

**Change To:**
```python
TEAM_NAME = fetch_machine_name(ip_address)
if not TEAM_NAME:
    logger.error("Failed to retrieve machine name!")
    print("ERROR: Could not get machine name from Flask API")
    print(f"Make sure:")
    print(f"  1. Flask is running (python main.py)")
    print(f"  2. Machine IP {ip_address} is in database")
    print(f"  3. Base URL is correct: {MAIN_API_BASE_URL}")
    TEAM_NAME = "Unknown"
    # Optional: exit instead of continuing
    # sys.exit(1)
```

---

## 📋 Complete Checklist Before Running Raspberry Pi

- [ ] **Flask App Running**: `python main.py` is running on your server
- [ ] **Database Updated**: Ran migration to add IP columns
- [ ] **Machine IP in DB**: Your Raspberry Pi's IP is in the machines table
- [ ] **Base URL Updated**: MAIN_API_BASE_URL points to Flask server (not localhost, not wrong IP)
- [ ] **Port Correct**: Flask is on port 5000 (not 1250, not 8000)
- [ ] **Network Connectivity**: Raspberry Pi can ping Flask server
  ```bash
  # On Raspberry Pi
  ping 192.168.1.100  # Replace with your Flask server IP
  ```
- [ ] **API Test**: Curl test works from Raspberry Pi
  ```bash
  curl http://192.168.1.100:5000/api/events/machines/list
  ```

---

## 🧪 Debug Steps in Order

### 1. Test Network Connectivity
```bash
# On Raspberry Pi
ping 192.168.1.100  # Your Flask server IP

# Should see: bytes from 192.168.1.100: seq=0 ttl=64
```

### 2. Test API is Reachable
```bash
# On Raspberry Pi
curl http://192.168.1.100:5000/api/events/machines/list

# Should return JSON like: {"machines": [...]}
```

### 3. Check Database Has IP
```sql
-- Run in MySQL
SELECT machine_code, ip_address FROM machines WHERE ip_address IS NOT NULL;

-- Should show:
-- M001 | 10.110.30.15
```

### 4. Test API with Specific IP
```bash
# On Raspberry Pi
curl -X POST http://192.168.1.100:5000/api/events/get_machine_name \
  -H "Content-Type: application/json" \
  -d '{"ip_address": "10.110.30.15"}'

# Should return: {"machine_name": "M001", ...}
```

### 5. Run Raspberry Pi with Debug
```bash
# Add debug prints to raspberrycode.py (see CHANGE 2 above)
# Then run:
python raspberrycode.py

# You should see:
# DEBUG: Attempting to reach: http://192.168.1.100:5000/api/events/get_machine_name
# DEBUG: Sending IP: 10.110.30.15
# DEBUG: Response status: 200
# SUCCESS: Got machine name: M001
# System started for M001
```

---

## ❌ Common Errors & Solutions

### Error: "Connection refused"
```
ERROR: Connection failed - [Errno 111] Connection refused
```
**Solution**: 
- Flask not running (start it: `python main.py`)
- Wrong IP address in MAIN_API_BASE_URL
- Wrong port (should be :5000, not :1250)

### Error: "Name or service not known"
```
ERROR: Connection failed - Name or service not known
```
**Solution**:
- Wrong IP address (typo in MAIN_API_BASE_URL)
- Raspberry Pi not on same network as Flask server
- Check network connectivity: `ping 192.168.1.100`

### Error: "404 Not Found"
```
Response status: 404
ERROR: Server returned 404
```
**Solution**:
- API endpoint doesn't exist (blueprint not registered)
- Check Flask app logs for startup errors
- Make sure machine_events.py exists in app/routes/

### Machine Shows "Unknown"
```
System started for Unknown
```
**Solution**:
- IP not in database (run: `UPDATE machines SET ip_address='10.110.30.15' WHERE machine_code='M001'`)
- database IP doesn't match Raspberry Pi IP
- API endpoint returning 404

---

## ✅ What You Should See When It Works

**In Raspberry Pi terminal:**
```
System started for M001. Waiting for sensor triggers...
[sensor trigger]
Downtime alert triggered
Select event type...
[button pressed]
User ID Entered
Event downtime started
Downtime Started
[etc...]
```

**In Flask logs:**
```
POST /api/events/get_machine_name 200
Downtime started for M001
Event sent successfully: downtime for M001
```

**In database:**
```
SELECT * FROM machine_events ORDER BY event_start_time DESC LIMIT 1;
+----+------------+--------------+----------+--------------+-------+-------+...
| id | machine_id | machine_name | event_type | event_status | ... |
+----+------------+--------------+----------+--------------+-------+-------+...
| 1  | 1          | M001         | downtime   | started     | ... |
```

---

## 🚀 Quick Reference

| Problem | Command to Fix |
|---------|---|
| Can't reach API | `curl http://FLASK_IP:5000/api/events/machines/list` |
| No machines with IP | `UPDATE machines SET ip_address='10.110.30.15' WHERE machine_code='M001';` |
| Wrong base URL | Edit line 44 in raspberrycode.py |
| Flask not running | `python main.py` |
| Need diagnostics | `python diagnose_rpi_issues.py` |

---

## 📝 Summary

**Usually just need to change:**

1. **Line 44 in raspberrycode.py**:
   ```python
   MAIN_API_BASE_URL = "http://[YOUR_FLASK_IP]:5000/api"
   ```

2. **Add IP to machines in database**:
   ```sql
   UPDATE machines SET ip_address='10.110.30.15' WHERE machine_code='M001';
   ```

3. **Make sure Flask is running**:
   ```bash
   python main.py
   ```

If still not working, run:
```bash
python diagnose_rpi_issues.py
```

This will tell you exactly what's wrong!

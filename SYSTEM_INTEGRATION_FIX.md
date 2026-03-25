# 🔧 Complete System Integration Fix Guide

## Problem Summary
"Machine unknown" error = Raspberry Pi can't reach Flask API or can't find its machine code in database.

---

## ✅ STEP 1: Verify Flask is Running

### On Your Server (where Flask app is):
```bash
# Check if Flask is running
ps aux | grep main.py

# If NOT running, start it:
cd /path/to/app
python main.py

# You should see:
# * Serving Flask app 'app'
# * Running on http://127.0.0.1:5000
# * Debugger is active!
```

**✓ Pass Condition**: Flask app is running and showing HTTP server output

---

## ✅ STEP 2: Get Your Server IP Address

### Find Flask Server IP:
```bash
# On Linux/Mac:
ifconfig | grep "inet " | grep -v 127.0.0.1

# On Windows (run in PowerShell):
ipconfig | findstr /i "IPv4"

# On Raspberry Pi:
hostname -I
```

Write down: **MY_FLASK_SERVER_IP = ___________________**

Example: `192.168.1.100` or `10.110.30.50`

**❌ WRONG**: Don't use `127.0.0.1` or `localhost` - these are local only!  
**❌ WRONG**: Don't use `http://10.110.30.15:1250` - this is old port number!

---

## ✅ STEP 3: Test Network Connectivity

### From Raspberry Pi, test if it can reach Flask server:
```bash
# On Raspberry Pi
ping 192.168.1.100

# Should see:
# PING 192.168.1.100 (192.168.1.100) 56(84) bytes of data.
# 64 bytes from 192.168.1.100: icmp_seq=1 ttl=64 time=2.5ms
# 64 bytes from 192.168.1.100: icmp_seq=1 ttl=64 time=1.8ms
```

**✓ Pass Condition**: Gets ping response (not "Network unreachable" or "Destination host unreachable")

---

## ✅ STEP 4: Test Flask API Endpoint

### From Raspberry Pi, test if API is working:
```bash
# On Raspberry Pi
curl http://192.168.1.100:5000/api/events/machines/list

# Should return JSON like:
# {
#   "machines": [
#     {"id": 1, "machine_code": "M001", "machine_name": "Machine 1", "ip_address": "10.110.30.15"},
#     {...}
#   ]
# }
```

**If you get error:**
- "Connection refused" → Flask not running (STEP 1)
- "Name or service not known" → Wrong IP address
- "404 Not Found" → API endpoint not available

**✓ Pass Condition**: Gets JSON response with machines array

---

## ✅ STEP 5: Verify Machine IP in Database

### Check if your Raspberry Pi's IP is recorded:
```sql
-- Login to MySQL and run:
USE maintenance_system_v2;

-- Get Raspberry Pi IP
SELECT machine_code, ip_address, machine_name, zone FROM machines;

-- Should show something like:
-- M001 | 10.110.30.15 | Machine 1 | Zone A
-- M002 | 10.110.30.16 | Machine 2 | Zone B
```

**If IP_ADDRESS column missing:**
- Run this SQL first:
```sql
ALTER TABLE machines ADD COLUMN ip_address VARCHAR(45) UNIQUE;
ALTER TABLE machines ADD COLUMN machine_name VARCHAR(100);
ALTER TABLE machines ADD COLUMN zone VARCHAR(100);
ALTER TABLE machines ADD INDEX idx_ip_address (ip_address);
```

**If machines have NULL ip_address:**
- Update them:
```sql
UPDATE machines SET ip_address='10.110.30.15', machine_name='M001' WHERE machine_code='M001';
UPDATE machines SET ip_address='10.110.30.16', machine_name='M002' WHERE machine_code='M002';
-- More machines...
```

**✓ Pass Condition**: All machines have IP addresses filled in

---

## ✅ STEP 6: Test Machine Name API

### From Raspberry Pi, test the specific endpoint:
```bash
# On Raspberry Pi (replace 10.110.30.15 with ACTUAL Raspberry Pi IP)
curl -X POST http://192.168.1.100:5000/api/events/get_machine_name \
  -H "Content-Type: application/json" \
  -d '{"ip_address": "10.110.30.15"}'

# Should return:
# {
#   "machine_id": 1,
#   "machine_name": "M001",
#   "machine_code": "M001",
#   "department": "Production",
#   "zone": "Zone A"
# }
```

**If you get:**
- `{"error": "Machine with this IP not found"}` → IP not in database (STEP 5)
- Empty response or 404 → API endpoint not available in Flask app

**✓ Pass Condition**: Returns machine code for the IP address

---

## ✅ STEP 7: Update Raspberry Pi Code

### Edit raspberrycode.py:

**Find line 44** (around there):
```python
MAIN_API_BASE_URL = "http://10.110.30.15:1250/api"  # ← WRONG
```

**Change to:**
```python
MAIN_API_BASE_URL = "http://192.168.1.100:5000/api"  # ← Your Flask IP
```

**Also add debug logging** (find `def fetch_machine_name()` and add):
```python
def fetch_machine_name(ip_address):
    try:
        url = f"{MAIN_API_BASE_URL}/events/get_machine_name"
        data = {"ip_address": ip_address}
        
        print(f"[DEBUG] Fetching machine name from: {url}")
        print(f"[DEBUG] Sending IP: {ip_address}")
        
        response = requests.post(url, json=data, timeout=5)
        
        print(f"[DEBUG] Response status: {response.status_code}")
        print(f"[DEBUG] Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            machine_name = result.get("machine_name")
            print(f"[SUCCESS] Got machine: {machine_name}")
            return machine_name
        else:
            print(f"[ERROR] Server returned {response.status_code}")
            return None
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        return None
```

**✓ Pass Condition**: Base URL points to correct Flask server and port

---

## ✅ STEP 8: Run Raspberry Pi Test

### Execute raspberrycode.py:
```bash
# On Raspberry Pi
python raspberrycode.py

# You should see (with debug prints):
# [DEBUG] Fetching machine name from: http://192.168.1.100:5000/api/events/get_machine_name
# [DEBUG] Sending IP: 10.110.30.15
# [DEBUG] Response status: 200
# [DEBUG] Response: {"machine_name": "M001", ...}
# [SUCCESS] Got machine: M001
# System started for M001. Waiting for sensor triggers...
```

**If you see "Unknown":**
- Look at the DEBUG output to identify which step failed
- Go back to STEP 1-7 and fix

**✓ Pass Condition**: Sees "System started for M001" (not "Unknown")

---

## ✅ STEP 9: Test Event Sending

### Trigger an event on Raspberry Pi:
1. Ground the sensor pin (trigger downtime) OR press a button
2. Select event type when prompted
3. Enter user ID

**In Flask terminal, should see:**
```
POST /api/events/downtime/M001 201
Event saved successfully
```

**In database, check:**
```sql
SELECT * FROM machine_events 
WHERE machine_code = 'M001' 
ORDER BY event_start_time DESC 
LIMIT 5;
```

Should show recent events from Raspberry Pi.

**✓ Pass Condition**: Events appearing in database and Flask logs

---

## ✅ STEP 10: Verify on Dashboard

### Login to Flask app dashboard:
1. Go to `http://YOUR_FLASK_IP:5000`
2. Look for "Machine Status" card - should show M001 status
3. Click on machine history - should show recent events

**✓ Pass Condition**: Dashboard shows machine status and events

---

## 🧪 Troubleshooting Checklist

| Issue | Check | Fix |
|-------|-------|-----|
| "Machine unknown" | STEP 6 output | Check machine IP in database (STEP 5) |
| Can't reach API | STEP 4 result | Flask might not be running (STEP 1) |
| No events appearing | STEP 9 | Check API endpoint in Flask logs |
| Wrong IP shown | Confirm Raspberry Pi IP | Run `hostname -I` on Pi |
| 404 errors | STEP 4 response | Make sure `app/routes/machine_events.py` exists |
| Connection refused | STEP 4 response | Flask not running or wrong port |

---

## 📋 Quick Validation Commands

**All at once, test everything:**

### On Server (Flask):
```bash
# 1. Flask running?
ps aux | grep main.py

# 2. API working?
curl http://localhost:5000/api/events/machines/list

# 3. Database ready?
mysql -u root -p -e "USE maintenance_system_v2; SELECT machine_code, ip_address FROM machines LIMIT 5;"
```

### On Raspberry Pi:
```bash
# 1. Can reach server?
ping 192.168.1.100

# 2. API accessible?
curl http://192.168.1.100:5000/api/events/machines/list

# 3. Machine name endpoint?
curl -X POST http://192.168.1.100:5000/api/events/get_machine_name \
  -H "Content-Type: application/json" \
  -d '{"ip_address": "10.110.30.15"}'

# 4. What's my IP?
hostname -I
```

---

## 🆘 Still Not Working?

Run the diagnostic script:
```bash
python diagnose_rpi_issues.py
```

This will:
- ✓ Check Flask app is initialized
- ✓ Verify database has machines with IPs
- ✓ Test API endpoint works
- ✓ Check if events are being recorded

It will tell you EXACTLY which step is failing.

---

## ✅ Final Checklist

After following all steps, verify:

- [ ] Flask app running on correct port (5000)
- [ ] MAIN_API_BASE_URL updated in raspberrycode.py
- [ ] Machine IP addresses in database
- [ ] Raspberry Pi can ping Flask server
- [ ] API endpoint returns machine name for the IP
- [ ] raspberrycode.py starts without "Unknown"
- [ ] Events appear in database after triggers
- [ ] Dashboard shows machine status and events

---

## 🚀 If Everything Works!

Your system is now integrated:
- ✅ Raspberry Pi can identify itself to Flask
- ✅ Events are being sent and stored
- ✅ Dashboard shows real-time status
- ✅ Maintenance team can see what's happening
- ✅ System ready for production

Celebrate! 🎉

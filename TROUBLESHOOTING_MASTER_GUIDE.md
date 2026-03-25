# 🎯 Raspberry Pi Integration - Master Guide & Troubleshooting

## 📋 Quick Summary

**Problem**: "Machine unknown" - Raspberry Pi can't identify itself to Flask app

**Root Causes** (in order of likelihood):
1. **Wrong API URL** in raspberrycode.py (line 44 still points to old IP/port)
2. **Machine IP not in database** (ip_address column is NULL for your machines)
3. **Flask app not running** (no API to query)
4. **Network issue** (Raspberry Pi can't reach Flask server)
5. **Database not migrated** (ip_address column doesn't exist)

**Solution**: Follow the steps in this guide to identify and fix the exact issue.

---

## 🚀 Start Here: 3-Minute Quick Fix

If you just want to get it working, try this first:

### 1. Update raspberrycode.py (Line 44)

**Find**:
```python
MAIN_API_BASE_URL = "http://10.110.30.15:1250/api"
```

**Change to** (replace with your Flask server IP):
```python
MAIN_API_BASE_URL = "http://192.168.1.100:5000/api"
```

Get your IP:
```bash
# On your Flask server
ifconfig | grep "inet " | grep -v 127.0.0.1
# Example output: 192.168.1.100
```

### 2. Add Machine IP to Database

```sql
-- Login to MySQL
mysql -u root -p

-- Run this:
USE maintenance_system_v2;
UPDATE machines SET ip_address='10.110.30.15' WHERE machine_code='M001';
SELECT machine_code, ip_address FROM machines;
```

Get Raspberry Pi IP:
```bash
# On Raspberry Pi
hostname -I
# Example output: 10.110.30.15
```

### 3. Make Sure Flask is Running

```bash
# On your Flask server
python main.py

# Should see:
# * Running on http://127.0.0.1:5000
```

### 4. Test It

```bash
# On Raspberry Pi
python raspberrycode.py

# Should see:
# System started for M001
# NOT: System started for Unknown
```

**If it works**, you're done! ✅

**If it still shows "Unknown"**, follow the detailed guide below.

---

## 🔍 Detailed Troubleshooting Guide

### Level 1: Network Connectivity

**Test if Raspberry Pi can reach Flask server**:

```bash
# On Raspberry Pi
ping 192.168.1.100  # Your Flask server IP

# Should see:
# PING 192.168.1.100 (192.168.1.100) 56(84) bytes of data.
# 64 bytes from 192.168.1.100: icmp_seq=1 ttl=64 time=2.5ms
```

**If FAILED** (Network unreachable, Destination host unreachable):
- Check Raspberry Pi is connected to network: `ifconfig | grep inet`
- Check Flask server IP is correct
- Check both on same network (same subnet)
- Check firewall isn't blocking: `sudo ufw status`

---

### Level 2: Flask API Accessibility

**Test if API responds**:

```bash
# On Raspberry Pi
curl http://192.168.1.100:5000/api/events/machines/list

# Should see JSON:
# {"machines": [{"id": 1, "machine_code": "M001", ...}, ...]}
```

**If FAILED** (Connection refused, Name or service not known):
- Flask not running: Start it with `python main.py`
- Wrong IP address: Double-check with `ifconfig`
- Wrong port: Default is 5000, not 1250 or 8000
- Firewall blocking: Allow port 5000

**If FAILED** (Empty response, no data):
- Database has no machines: Add them as below
- Database machines don't have active status

---

### Level 3: Machine IP in Database

**Check if your machine's IP is recorded**:

```sql
-- On your server with MySQL
USE maintenance_system_v2;
SELECT machine_code, ip_address, status FROM machines;

-- Should show something like:
-- M001 | 10.110.30.15 | active
-- M002 | 10.110.30.16 | active
```

**If ip_address column is NULL**:
```sql
-- Add the IP address
UPDATE machines SET ip_address='10.110.30.15' WHERE machine_code='M001';
UPDATE machines SET ip_address='10.110.30.16' WHERE machine_code='M002';
-- More machines as needed...
```

**If ip_address column doesn't exist**:
```sql
-- Create it
ALTER TABLE machines ADD COLUMN ip_address VARCHAR(45) UNIQUE;
ALTER TABLE machines ADD COLUMN machine_name VARCHAR(100);
ALTER TABLE machines ADD COLUMN zone VARCHAR(100);
ALTER TABLE machines ADD INDEX idx_ip_address (ip_address);

-- Then add IPs
UPDATE machines SET ip_address='10.110.30.15' WHERE machine_code='M001';
```

**If machines table doesn't exist**:
- Database migration wasn't run
- Run: `python main.py` (should auto-create tables)
- Or manually run CREATE TABLE statements

---

### Level 4: API Endpoint Test

**Test the specific endpoint Raspberry Pi uses**:

```bash
# On Raspberry Pi (or any machine on same network)
curl -X POST http://192.168.1.100:5000/api/events/get_machine_name \
  -H "Content-Type: application/json" \
  -d '{"ip_address": "10.110.30.15"}'

# Should return:
# {
#   "machine_name": "M001",
#   "machine_id": 1,
#   "department": "Production",
#   "zone": "Zone A"
# }
```

**If FAILED** (404 Not Found):
- API route not registered in Flask
- Check `app/routes/machine_events.py` exists
- Check `app/__init__.py` has: `from app.routes.machine_events import events_bp`
- Check: `app.register_blueprint(events_bp)`

**If FAILED** (404 Machine not found):
- Machine IP not in database (see Level 3 above)
- IP in database doesn't match IP being sent
- Get Raspberry Pi IP: `hostname -I` on Pi
- Make sure it matches exactly in database

**If FAILED** (500 Server Error):
- Database connection issue
- Run `python diagnose_rpi_issues.py` for details

---

### Level 5: Verify Raspberry Pi IP Address

**Make sure you're using the CORRECT Raspberry Pi IP**:

```bash
# On Raspberry Pi
hostname -I

# Output: 10.110.30.15 192.168.1.50  (might show multiple)
# Use the one that matches your network

# Get the IP on main interface
ip addr show | grep "inet " | grep -v 127.0.0.1
```

**Common mistakes**:
- ❌ Using `127.0.0.1` (localhost - doesn't work from other machines)
- ❌ Using `192.168.1.1` (gateway, not the Pi)
- ❌ Using wrong interface (eth0 vs wlan0)

---

### Level 6: Flask App Initialization

**Verify Flask app starts correctly**:

```bash
# On your Flask server
python main.py

# Should see output like:
# * Serving Flask app 'app'
# * Environment: development
# * Debug mode: on
# * Running on http://127.0.0.1:5000
# * Debugger is active!
```

**Common issues**:
- Port already in use: `Address already in use`
  - Kill it: `lsof -ti:5000 | xargs kill -9`
  - Or use different port: `FLASK_ENV=production python main.py` 

- Import errors: `ModuleNotFoundError`
  - Install requirements: `pip install -r requirements.txt`
  - Check Python path: `export PYTHONPATH=/path/to/app:$PYTHONPATH`

- Database errors: `sqlalchemy.exc.Error`
  - Check database is running and accessible
  - Check credentials in `config.py`

---

## 🧬 What Changed in the Code

### Python Change: raspberrycode.py Line 44

**Before** (WRONG - works only locally):
```python
MAIN_API_BASE_URL = "http://10.110.30.15:1250/api"
```

**After** (CORRECT - works from any network):
```python
MAIN_API_BASE_URL = "http://192.168.1.100:5000/api"  # Replace with YOUR Flask IP
```

### Database Changes: machines table

**New Columns Added**:
```sql
ALTER TABLE machines ADD COLUMN ip_address VARCHAR(45) UNIQUE;
ALTER TABLE machines ADD COLUMN machine_name VARCHAR(100);
ALTER TABLE machines ADD COLUMN zone VARCHAR(100);
```

**Sample Data**:
```sql
UPDATE machines 
SET ip_address='10.110.30.15', 
    machine_name='M001', 
    zone='Zone A' 
WHERE machine_code='M001';
```

### Flask Changes: machine_events.py

**New Endpoint Added**:
```python
@events_bp.route('/events/get_machine_name', methods=['POST'])
def get_machine_name():
    """Get machine name and code from IP address"""
    ip_address = request.json.get('ip_address')
    machine = Machine.query.filter_by(ip_address=ip_address).first()
    return jsonify({
        "machine_name": machine.machine_code,
        "machine_id": machine.id
    })
```

This is what Raspberry Pi calls to identify itself when it starts.

---

## 🆘 Automated Diagnostics

If you're stuck, run this:

```bash
python diagnose_rpi_issues.py
```

This will:
- ✓ Check Flask app is initialized
- ✓ Test database has machines with IP addresses
- ✓ Test API endpoint returns correct response
- ✓ Check if events are being recorded
- ✓ Tell you EXACTLY what's wrong and how to fix it

---

## 📋 Complete Checklist

Before running Raspberry Pi, verify all of these:

### Code Changes
- [ ] raspberrycode.py line 44: Base URL updated to your Flask server
- [ ] Machine IP is the ACTUAL Raspberry Pi IP (from `hostname -I`)
- [ ] Flask server IP is correct (not localhost or wrong IP)

### Database Setup
- [ ] MySQL database is running
- [ ] `machines` table exists
- [ ] `machines` table has columns: `id`, `machine_code`, `ip_address`, `status`
- [ ] At least one machine exists with active status
- [ ] That machine has ip_address filled (not NULL)
- [ ] ip_address matches actual Raspberry Pi IP exactly
- [ ] `machine_events` table exists and is empty (initially)

### Flask App
- [ ] `app/routes/machine_events.py` file exists
- [ ] `app/__init__.py` imports and registers `events_bp`
- [ ] Flask starts without errors: `python main.py`
- [ ] API responds: `curl http://localhost:5000/api/events/machines/list`
- [ ] Machine name endpoint works (see Level 4 test above)

### Network
- [ ] Raspberry Pi connected to network: `ifconfig`
- [ ] Can ping Flask server: `ping FLASK_IP`
- [ ] Can reach API: `curl http://FLASK_IP:5000/api/events/machines/list`
- [ ] Firewall allows port 5000 (or whatever Flask port)

### Raspberry Pi
- [ ] Raspberry Pi can reach Flask server
- [ ] Raspberry Pi knows its own IP: `hostname -I`
- [ ] That IP is in database
- [ ] Code has debug prints (optional but helpful)

---

## ✅ Testing Sequence

Follow in order:

1. **Terminal 1** - Start Flask:
   ```bash
   python main.py
   ```

2. **Terminal 2** - Test connectivity:
   ```bash
   curl http://localhost:5000/api/events/machines/list
   # Should return machines with IPs
   ```

3. **Terminal 2** - Test machine name endpoint:
   ```bash
   curl -X POST http://localhost:5000/api/events/get_machine_name \
     -H "Content-Type: application/json" \
     -d '{"ip_address": "10.110.30.15"}'
   # Should return machine details
   ```

4. **Raspberry Pi** - Run the code:
   ```bash
   python raspberrycode.py
   # Should show: System started for M001 (not Unknown)
   ```

5. **Raspberry Pi** - Trigger an event:
   - Ground sensor or press button
   - Select event type
   - Enter user ID

6. **Terminal 2** - Check database:
   ```bash
   # Or run: python check_events_quick.py M001
   mysql
   USE maintenance_system_v2;
   SELECT * FROM machine_events ORDER BY id DESC LIMIT 1;
   # Should show the event you just triggered
   ```

7. **Dashboard** - Verify:
   - Login to Flask web interface
   - Check Machine Status card shows M001
   - Check recent events from Raspberry Pi

---

## 🎯 Success Indicators

After following this guide, you should see:

**On Raspberry Pi Terminal**:
```
[DEBUG] Sending IP: 10.110.30.15
[DEBUG] Response status: 200
[SUCCESS] Got machine: M001
System started for M001. Waiting for sensor triggers...
```

**In Flask Terminal**:
```
127.0.0.1 - - [Date] "POST /api/events/get_machine_name HTTP/1.1" 200 -
127.0.0.1 - - [Date] "POST /api/events/downtime/M001 HTTP/1.1" 201 -
```

**In Database**:
```
SELECT event_type, COUNT(*) FROM machine_events GROUP BY event_type;
-- Shows downtime, maintenance, break events from Raspberry Pi
```

**On Dashboard**:
- Machine Status card shows M001 with current status
- Recent events listed
- Downtime duration showing
- No "Unknown" machines

---

## 🚀 Troubleshooting Resources

| File | Purpose |
|------|---------|
| `SYSTEM_INTEGRATION_FIX.md` | Step-by-step fix guide (10 detailed steps) |
| `RASPBERRY_CODE_CHANGES.md` | What to change in raspberrycode.py |
| `FLASK_COMPONENTS_VERIFICATION.md` | Verify Flask app is set up correctly |
| `diagnose_rpi_issues.py` | Automated diagnostic script |
| `check_events_quick.py` | Quick command to check events |
| `query_machine_events.py` | Interactive event viewer |

---

## 📞 Getting Help

If you're still stuck:

1. **Run diagnostics**:
   ```bash
   python diagnose_rpi_issues.py
   ```

2. **Check logs**:
   - Flask terminal output (running Flask)
   - Raspberry Pi terminal output (running code)
   - MySQL error logs

3. **Use the test tools**:
   ```bash
   # Check machine IP
   curl -X POST http://localhost:5000/api/events/get_machine_name \
     -H "Content-Type: application/json" \
     -d '{"ip_address": "10.110.30.15"}'
   
   # Check recent events
   python check_events_quick.py M001
   ```

4. **Verify each component**:
   - ✓ Network: `ping FLASK_IP`
   - ✓ API: `curl http://FLASK_IP:5000/api/events/machines/list`
   - ✓ Database: `SELECT * FROM machines;`
   - ✓ Flask logs: Look for error messages

---

## 🎉 When It Works

Once integrated, you'll have:
- ✅ Real-time machine status visible on dashboard
- ✅ Event history automatically recorded
- ✅ Downtime tracking with duration
- ✅ Maintenance team can monitor from anywhere
- ✅ Complete audit trail of all actions

Congratulations! Your system is now fully operational! 🚀

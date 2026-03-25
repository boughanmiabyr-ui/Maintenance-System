# 🔧 Maintenance Event Not Ending - Root Cause & Fix

## Your Problem

When you pressed the maintenance button to **END** the maintenance:
- ✓ You selected an end user ID
- ✓ You selected a maintenance type
- ✓ Raspberry Pi reset the system
- ✗ But `reset_maintenance` endpoint was NEVER called

**Evidence**: Database shows `event_status='started'` and `event_end_time=NULL`

---

## 🎯 Root Cause

There are 2 possible causes:

### Cause 1: reset_system Not Called Properly
When the maintenance button is pressed the 2nd time (to END):
1. It should call `reset_system("maintenance", end_user_id, end_comment, breakdown_type)`
2. This should trigger: `send_event_async("reset_maintenance", ...)`
3. Which should POST to: `/api/events/reset_maintenance/MACH001`

If this chain breaks anywhere, the end event isn't recorded.

### Cause 2: API Call Failed Silently  
Even if reset_maintenance was called, if:
- Network timeout occurs
- Flask endpoint returns error
- The async thread failed

Then the event wouldn't be recorded.

---

## ✅ How to Fix It

### Step 1: Manually End the Event (Quick Fix)

If you need to end the existing maintenance event immediately:

```bash
# From your laptop
curl -X POST http://192.168.137.1:5000/api/events/reset_maintenance/MACH001 \
  -H "Content-Type: application/json" \
  -d '{
    "end_user_id": "1414",
    "end_comment": "Maintenance completed",
    "breakdown": "Maintenance"
  }'

# Should return:
# {"status": "success", "message": "Maintenance ended for MACH001"}
```

Then verify in database:
```sql
SELECT event_status, event_end_time, duration_seconds, end_user_id 
FROM machine_events 
WHERE machine_id = 1 
ORDER BY id DESC 
LIMIT 1;

-- Should show:
-- event_status: 'ended'
-- event_end_time: (current time)
-- duration_seconds: (calculated)
-- end_user_id: '1414'
```

---

### Step 2: Check Why reset_system Didn't Call the API

Look at **raspberrycode.py logs** to see what happened:

```bash
# On Raspberry Pi or see the log file
tail -50 button_log.log | grep -i "maintenance\|reset"

# Should show:
# 1. "Maintenance button PRESSED"
# 2. "Enter User ID to end maintenance"
# 3. "Select maintenance type" (or similar)
# 4. "Calling reset_system with" 
# 5. "Event reset_maintenance ended"
```

**If you see steps 1-4 but NOT step 5**, then:
- reset_system was called
- But API call failed

**If you see nothing**, then:
- Button press wasn't detected
- Or maintenance_state wasn't "arrived"

---

### Step 3: Enable Debug Logging in Raspberry Pi Code

Add this to raspberrycode.py in the `send_event_async()` function for better visibility:

Find this around line 195:
```python
def send_event_async(event_type, duration=None, ...):
    ...
    def send_request():
        try:
            url = f"{MAIN_API_BASE_URL}/events/{event_type}/{TEAM_NAME}"
            data = {...}
            logger.info(f"Sending event to {url} - Details: {json.dumps(data)}")
            response = requests.post(url, json=data, timeout=5)
```

Add these debug lines:
```python
def send_event_async(event_type, duration=None, ...):
    ...
    def send_request():
        try:
            url = f"{MAIN_API_BASE_URL}/events/{event_type}/{TEAM_NAME}"
            data = {...}
            
            # ADD THESE DEBUG LINES:
            print(f"\n[DEBUG] Sending {event_type} event")
            print(f"[DEBUG] URL: {url}")
            print(f"[DEBUG] TEAM_NAME: {TEAM_NAME}")
            print(f"[DEBUG] Data: {data}")
            
            logger.info(f"Sending event to {url} - Details: {json.dumps(data)}")
            response = requests.post(url, json=data, timeout=5)
            
            # ADD THESE DEBUG LINES:
            print(f"[DEBUG] Response Status: {response.status_code}")
            print(f"[DEBUG] Response Text: {response.text}")
```

This will show in the Raspberry Pi terminal exactly what's being sent and what response comes back.

---

### Step 4: Check Reset System State

In raspberrycode.py, the maintenance has a state machine:
- `maintenance_state = None` → Not in maintenance
- `maintenance_state = "started"` → Maintenance just started, waiting for arrival
- `maintenance_state = "arrived"` → Technician arrived, press again to END

If the button press doesn't end the event, check:
```python
# Around line 784-795 in raspberrycode.py
elif maintenance_state == "arrived":  # ← Make sure this check exists
    awaiting_user_id = True
    end_user_id = get_user_id_from_input(...)
    ...
    reset_system(start_comment.lower(), end_user_id, ...)
```

If `maintenance_state` is still "started" instead of "arrived", the condition won't match and reset won't be called.

---

## 📊 Check Current Event Status

### In Flask App Dashboard

1. Go to **Machine Status Monitor** card on dashboard
2. Click **"View Events"** button on your machine card
3. Should see the maintenance event in the modal
4. Status should show: **Active** (if not ended) or **Ended** (if fixed)

If you don't see any button:
- Make sure you're logged in
- Make sure you have access to the machine_status view
- Check browser console for JavaScript errors

### In Database

```sql
-- See all maintenance events
SELECT id, event_type, event_status, event_start_time, event_end_time, 
       duration_seconds, end_user_id 
FROM machine_events 
WHERE machine_id = 1 
AND event_type = 'maintenance'
ORDER BY event_start_time DESC;

-- See the problematic one:
SELECT * FROM machine_events 
WHERE machine_id = 1 
AND event_status = 'started'
LIMIT 1;
```

---

## 🔍 Step-by-Step Diagnosis

### If You're Not Sure What's Wrong

Follow this checklist:

1. **Check Raspberry Pi logs**
   ```bash
   tail -100 button_log.log | grep -i "maintenance"
   ```
   - Look for: "Maintenance button PRESSED", "Calling reset_system"

2. **Check Flask logs**
   ```bash
   # Look at Flask terminal output when you pressed the button
   # Should show: POST /api/events/reset_maintenance/MACH001
   ```
   - If NOT there → Raspberry Pi didn't call it
   - If there with 200 → Call succeeded but didn't update DB

3. **Check Database**
   ```sql
   SELECT event_status, event_end_time 
   FROM machine_events WHERE machine_id = 1 
   ORDER BY id DESC LIMIT 1;
   ```
   - Status = 'started' → reset_maintenance not called
   - Status = 'ended' → It's fixed!

4. **Test API endpoint manually**
   ```bash
   curl -X POST http://192.168.137.1:5000/api/events/reset_maintenance/MACH001 \
     -H "Content-Type: application/json" \
     -d '{"end_user_id": "1414"}'
   ```
   - Works? → Then Raspberry Pi isn't calling it
   - 404? → Flask endpoint missing
   - 500? → Database error

---

## 🛠️ Common Issues & Fixes

### Issue 1: maintenance_state Never Changes from "started" to "arrived"

**Symptom**: Button pressed but nothing happens  
**Cause**: `maintenance_arrival` endpoint might not be updating maintenance_state  
**Fix**: Add this to Flask's `maintenance_arrival` endpoint:
```python
# In app/routes/machine_events.py
# After creating the maintenance_arrival event, also ensure
# MachineStatus is updated to show maintenance is happening
status.current_status = 'maintenance'
status.status_since = datetime.utcnow()
```

### Issue 2: send_event_async Throws Exception

**Symptom**: Button pressed, but API call fails silently  
**Cause**: TEAM_NAME might be None or network issue  
**Fix**: Check in reset_system function:
```python
if TEAM_NAME is None:
    logger.error("Cannot send event: TEAM_NAME is None!")
    print("ERROR: TEAM_NAME is not set - cannot send reset event")
    return  # Don't call reset_system if TEAM_NAME is None
```

### Issue 3: Response Timeout

**Symptom**: No response from Flask when button pressed  
**Cause**: Network latency or Flask not running  
**Fix**: Increase timeout in raspberrycode.py:
```python
# Change from 5 seconds to 10 seconds
response = requests.post(url, json=data, timeout=10)  # ← Changed from 5 to 10
```

---

## ✅ After Fix - Verify It Works

### Test Sequence

1. **Trigger new maintenance event** (on Raspberry Pi)
   - Press maintenance button
   - Select user
   - Select maintenance type

2. **Check Flask logs**
   - Should see: `POST /api/events/maintenance/MACH001 201`

3. **Press button again to END**
   - Select user
   - Add comment

4. **Check Flask logs again**
   - Should see: `POST /api/events/reset_maintenance/MACH001 200`

5. **Check Database**
   ```sql
   SELECT event_status, event_end_time, duration_seconds 
   FROM machine_events 
   ORDER BY id DESC LIMIT 1;
   ```
   - Should show: event_status='ended', event_end_time=(time), duration_seconds=(number)

6. **Check Dashboard**
   - View Events modal should show maintenance event
   - Status should be **Ended** (green badge)

---

## 📝 Summary

| Step | Action |
|------|--------|
| 1 | Manually end event via API (quick fix) |
| 2 | Check Raspberry Pi/Flask logs for what happened |
| 3 | Add debug logging to see what's being sent |
| 4 | Verify maintenance_state changes from "started" to "arrived" |
| 5 | Test new event end-to-end |
| 6 | View in dashboard to confirm |

**Expected Result**: Maintenance events now have proper start AND end times, and you can view them in the Machine Status Monitor with the "View Events" button.

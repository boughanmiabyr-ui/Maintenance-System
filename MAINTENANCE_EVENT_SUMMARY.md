# 🔴 Maintenance Event Issue - Complete Summary

## Your Situation

### What You See in Database
```
event_id:  1
event_type: 'maintenance'
event_status: 'started'  ← Stuck here!
start_user_id: 1414
end_user_id: NULL
event_start_time: 2026-03-16 11:37:47
event_end_time: NULL  ← Never set!
duration_seconds: NULL
```

### What Should Have Happened
```
1. Machine starts maintenance
2. Event recorded: event_status='started' ✓
3. You press button to END maintenance
4. reset_maintenance endpoint called
5. Event updated: event_status='ended' ✗ DIDN'T HAPPEN
6. event_end_time set ✗ DIDN'T HAPPEN
7. duration_seconds calculated ✗ DIDN'T HAPPEN
```

---

## 🔍 Root Cause: reset_maintenance Never Called

When you pressed the button to **end** maintenance:
- ✓ You were asked for end user ID
- ✓ Raspberry Pi should have called: `POST /api/events/reset_maintenance/MACH001`
- ✗ But Flask logs show NO such call was made

**Evidence**: No line in Flask console showing `POST /api/events/reset_maintenance/MACH001`

---

## ✅ Solution: 4 Steps

### Step 1: View Events in Dashboard (You Said "No Button to Display")

**Actually, the button EXISTS** - You just need to find it:

1. **Go to Dashboard** → Main page after login
2. **Look for "Machine Status Monitor" card** (cyan/turquoise color, heartbeat icon)
3. Click into it
4. You'll see your machine cards (MACH001, etc.)
5. Each card has a blue button: **"View Events"**
6. Click that button → Modal pops up showing all events

**If you don't see this card**:
- Make sure you're logged in as admin/supervisor
- The card should be visible by default after login

---

### Step 2: Manually End the Stuck Event (Right Now)

To fix the existing maintenance event immediately:

```bash
# Run this on your laptop (PowerShell)
curl -X POST http://192.168.137.1:5000/api/events/reset_maintenance/MACH001 `
  -H "Content-Type: application/json" `
  -d '{"end_user_id":"1414", "end_comment":"Maintenance completed"}'

# Expected response:
# {"status":"success","message":"Maintenance ended for MACH001"}
```

**Verify it worked**:
```bash
# Check database
mysql -u root -p

USE maintenance_system_v2;
SELECT event_status, event_end_time, duration_seconds 
FROM machine_events 
WHERE event_type='maintenance' 
ORDER BY id DESC LIMIT 1;

# Should now show:
# event_status='ended'
# event_end_time=(current time)
# duration_seconds=(some number)
```

---

### Step 3: Check Why reset_maintenance Wasn't Called

**Check Raspberry Pi logs**:
```bash
# On Raspberry Pi
tail -50 button_log.log | grep -i "maintenance\|reset"

# Look for:
# "Maintenance button PRESSED"
# "Calling reset_system"
# "Sending event to"
```

**Check Flask logs**:
- Look at the Flask terminal when you pressed the button
- Should show: `POST /api/events/reset_maintenance/MACH001`
- If NOT there → Raspberry Pi isn't calling it

---

### Step 4: Enable Debug to Find the Issue

Edit `raspberrycode.py` around line 195 in `send_event_async()`:

**Find this**:
```python
logger.info(f"Sending event to {url} - Details: {json.dumps(data)}")
response = requests.post(url, json=data, timeout=5)
```

**Add these lines after**:
```python
print(f"[SEND] Event: {event_type}")
print(f"[SEND] URL: {url}")
print(f"[SEND] TEAM_NAME: {TEAM_NAME}")
print(f"[RESPONSE] Status: {response.status_code}")
print(f"[RESPONSE] Text: {response.text}")
```

This will show in Raspberry Pi terminal exactly what's happening.

---

## 📊 How to View Events (Dashboard Navigation)

### Path to View Maintenance Events

```
Dashboard
├─ Machine Status Monitor (cyan card with heartbeat icon)
│  └─ Click on MACH001 card
│     └─ Click "View Events" button (blue)
│        └─ Modal opens showing:
│           ├─ event_type
│           ├─ start_time
│           ├─ duration
│           └─ status (Active/Ended/Cancelled)
```

### What You Should See in Modal

| Type | Start Time | Duration | Status |
|------|-----------|----------|--------|
| maintenance | 2026-03-16 11:37:47 | 5 min | **Ended** ✓ |

If Status shows **Active** (yellow badge):
- Event is still ongoing
- reset_maintenance wasn't called yet
- Use Step 2 above to manually end it

If no modal opens or no events show:
- Check browser console (F12) for errors
- Make sure you're logged in
- Try refreshing the page

---

## 🧪 Test the Full Lifecycle

To make sure it works correctly next time:

### 1. Trigger New Maintenance Event
- Press maintenance button on Raspberry Pi
- Enter user ID: `1414`
- Select maintenance type: `Maintenance` (or similar)
- LCD should show: "Maintenance Arrived\nPress to End"

### 2. Check Flask Logs
Should see:
```
POST /api/events/maintenance/MACH001 201 CREATED
```

### 3. End the Event
- Press maintenance button again
- Enter user ID: `1414`
- Enter comment or press Enter

### 4. Check Flask Logs Again
Should see:
```
POST /api/events/reset_maintenance/MACH001 200 OK
```

### 5. Check Database
```sql
SELECT event_type, event_status, event_end_time, duration_seconds
FROM machine_events
WHERE event_type = 'maintenance'
ORDER BY id DESC LIMIT 2;

-- Should show:
-- maintenance | ended | (timestamp) | (number)
-- reset_maintenance | - | - | -
```

Or you might see them as a single event:
```sql
-- maintenance | ended | timestamp | duration_seconds
```

### 6. View in Dashboard
- Go to Machine Status Monitor
- Click View Events on MACH001
- Should see maintenance event with Status: **Ended** (green badge)

---

## ⚠️ Common Issues & Quick Fixes

| Issue | Check | Fix |
|-------|-------|-----|
| Can't find View Events button | Are you in "Machine Status Monitor" card? | Go to Dashboard → Machine Status Monitor → Click card |
| Modal opens but shows "No events" | Are there any events at all? | Check database: `SELECT COUNT(*) FROM machine_events` |
| Modal shows event but status is "Active" | Did reset_maintenance get called? | Follow Step 2 to manually end |
| Flask not responding to reset | Is Flask running? | Check: `python main.py` |
| Got curl error "Cannot reach Flask" | Is IP/port correct? | Check your laptop IP: `ipconfig \| findstr IPv4` |

---

## 🎯 Most Likely Problem

Based on your data, the most likely issue is:

**Raspberry Pi's reset_system function is being called, but:**
1. `TEAM_NAME` might be None → Event not sent
2. `maintenance_state` is still "started" instead of "arrived" → Condition not matched
3. Network timeout → API call failed silently
4. Exception in send_event_async → Logged to file, not shown in terminal

**To diagnose which specific issue**:
1. Run the diagnostic script: `bash diagnose_maintenance_issue.sh`
2. Check Raspberry Pi logs for print output (if you add debug lines)
3. Check Flask logs for API call attempts

---

## 🔧 Next Steps

1. **Try Step 1**: Go to dashboard and find "Machine Status Monitor" card
2. **Try Step 2**: Manually end the event via curl command
3. **Verify**: Check database and dashboard that event now shows as "ended"
4. **Enable Debug**: Add print statements to Raspberry Pi code
5. **Test Again**: Trigger new maintenance event and verify full lifecycle
6. **Report Back**: If still issues, share:
   - Raspberry Pi terminal output (after pressing button)
   - Flask terminal output (after pressing button)
   - Database query result

---

## 📝 Summary

| Component | Status | Fix |
|-----------|--------|-----|
| **Database Event** | Stuck at 'started' | Manually end via curl |
| **Raspberry Pi Call** | Not being made | Add debug logging, check logs |
| **Dashboard View** | Button exists | Go to Machine Status Monitor card |
| **API Endpoint** | Working | Tested manually with curl |
| **Next Maintenance** | Should work better after debug | Enable logging, test lifecycle |

**Priority**: Fix the current event (Step 2), then enable debugging for next one (Step 4).

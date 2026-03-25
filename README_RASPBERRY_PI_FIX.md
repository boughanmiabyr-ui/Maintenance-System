# 📚 Raspberry Pi Integration - Complete Documentation Index

## 🎯 Your Problem

Raspberry Pi shows "Machine Unknown" with no events or status reaching the Flask app.

## 📖 Documentation Created

I've created comprehensive guides to help you fix this issue. Here's what each document does:

---

## 🚀 START HERE

### 1. **TROUBLESHOOTING_MASTER_GUIDE.md** ← START HERE FIRST
**What it is**: Complete overview of the problem, quick fixes, and detailed troubleshooting

**When to use**:
- You want to understand what went wrong
- You want a 3-minute quick fix first
- You need systematic troubleshooting in 6 levels
- You're stuck and need a roadmap

**Contains**:
- Quick summary of root causes
- 3-minute quick fix attempt
- 6-level troubleshooting guide
- Complete checklist
- Testing sequence
- Success indicators

**Read this first!** ⭐

---

## 🔧 FIXING GUIDES

### 2. **SYSTEM_INTEGRATION_FIX.md**
**What it is**: Step-by-step guide with 10 detailed fix steps

**When to use**:
- You want detailed, numbered instructions
- You're following step-by-step
- Each step has verification commands

**Contains**:
- STEP 1: Verify Flask is running
- STEP 2: Get Flask server IP
- STEP 3: Test network connectivity
- STEP 4: Test Flask API endpoint
- STEP 5: Verify machine IP in database
- STEP 6: Test machine name API
- STEP 7: Update Raspberry Pi code
- STEP 8: Run Raspberry Pi test
- STEP 9: Test event sending
- STEP 10: Verify on dashboard

**Use this for detailed step-by-step execution!** 

---

### 3. **RASPBERRY_CODE_CHANGES.md**
**What it is**: Detailed guide on what to change in raspberrycode.py

**When to use**:
- You want to know what code changes are needed
- You want to add debug logging
- You want common error solutions

**Contains**:
- CHANGE 1: Update Base URL (CRITICAL)
- CHANGE 2: Add debug logging
- CHANGE 3: Handle machine name errors
- Checklist before running
- Debug steps
- Common errors & solutions
- Quick reference table

**Use this to modify your Raspberry Pi code!** 

---

## ✅ VERIFICATION GUIDES

### 4. **FLASK_COMPONENTS_VERIFICATION.md**
**What it is**: Verification that your Flask app has all required components

**When to use**:
- Flask app not recognizing Raspberry Pi requests
- Getting 404 errors on API endpoints
- Want to verify Flask setup is complete
- Checking if database tables exist

**Contains**:
- Status of all required models (✅ VERIFIED)
- Status of all API routes (✅ VERIFIED)
- Blueprint registration status (✅ VERIFIED)
- Database table requirements
- How to verify each component
- Common issues and fixes
- Pre-launch checklist

**Use this to verify Flask is fully set up!**

---

## 🧪 AUTOMATED TOOLS

### 5. **diagnose_rpi_issues.py**
**What it is**: Automated diagnostic script that tests all 4 critical system areas

**How to use**:
```bash
python diagnose_rpi_issues.py
```

**What it does**:
- ✓ Tests Flask app initialization
- ✓ Tests database machines with IP
- ✓ Tests API endpoint functionality
- ✓ Tests if events are recorded
- ✓ Provides pass/fail summary
- ✓ Gives actionable next steps

**Use this when you want automated diagnosis!** 🤖

---

### 6. **check_events_quick.py**
**What it is**: Quick command-line tool to check events for a machine

**How to use**:
```bash
# Check specific machine
python check_events_quick.py M001

# Check all machines
python check_events_quick.py all

# Check active events only
python check_events_quick.py M001 --active
```

**What it shows**:
- Machine status
- Recent events with timestamps
- Event durations
- Downtime totals
- Color-coded output

**Use this to quickly check if events are being recorded!** ⚡

---

### 7. **query_machine_events.py**
**What it is**: Interactive menu-driven event query tool

**How to use**:
```bash
python query_machine_events.py
```

**What it does**:
- Interactive 6-option menu
- Query by machine code
- Custom date ranges
- Formatted output
- Event statistics

**Use this for interactive event exploration!** 📊

---

## 🎓 REFERENCE DOCUMENTS

### 8. **Previous Guides** (from earlier in this session)
- `RASPBERRY_PI_INTEGRATION_GUIDE.md` - API documentation
- `DASHBOARD_INTEGRATION_SUMMARY.md` - Dashboard structure
- `MACHINE_IP_EVENTS_GUIDE.md` - IP tracking reference
- `api_tester.html` - Interactive API testing

---

## 📋 Quick Decision Tree

**Choose your guide based on your situation:**

```
Is Raspberry Pi showing "Machine Unknown"?
│
├─ YES, and I want quick fix → TROUBLESHOOTING_MASTER_GUIDE.md (3-min section)
│
├─ YES, and I want step-by-step → SYSTEM_INTEGRATION_FIX.md (10 steps)
│
├─ YES, and I want code changes → RASPBERRY_CODE_CHANGES.md
│
├─ YES, and I want auto-diagnosis → python diagnose_rpi_issues.py
│
├─ I'm not sure what's wrong → TROUBLESHOOTING_MASTER_GUIDE.md (6 levels)
│
├─ Flask not responding to API → FLASK_COMPONENTS_VERIFICATION.md
│
├─ Want to check if events recorded → python check_events_quick.py M001
│
└─ Want interactive event viewer → python query_machine_events.py
```

---

## 🚀 Recommended Execution Path

### If You Just Want It Fixed Now (15 minutes):

1. Open **TROUBLESHOOTING_MASTER_GUIDE.md**
2. Try the "3-Minute Quick Fix" section
3. If it works, done! ✅
4. If not, run `python diagnose_rpi_issues.py`
5. Follow the specific fix recommended by diagnostics

### If You Like Detailed Instructions (30 minutes):

1. Read **SYSTEM_INTEGRATION_FIX.md** STEP 1-3 (verify Flask is running)
2. Read **RASPBERRY_CODE_CHANGES.md** to update raspberrycode.py
3. Follow STEP 4-10 in **SYSTEM_INTEGRATION_FIX.md**
4. Use **FLASK_COMPONENTS_VERIFICATION.md** to verify each component

### If You're Methodical (45 minutes):

1. Read **TROUBLESHOOTING_MASTER_GUIDE.md** (understand the problem)
2. Run **python diagnose_rpi_issues.py** (identify exact failure)
3. Follow the fix recommended by diagnostics
4. Verify with **check_events_quick.py** or **query_machine_events.py**
5. Use **FLASK_COMPONENTS_VERIFICATION.md** to ensure everything is correct

---

## 📊 Common Fixes Summary

| Issue | Quick Fix |
|-------|-----------|
| "Machine Unknown" | Update line 44 in raspberrycode.py with correct Flask IP |
| No events appearing | Add machine IP to database: `UPDATE machines SET ip_address='10.110.30.15' WHERE machine_code='M001'` |
| Flask not responding | Start Flask: `python main.py` |
| Can't reach API | Change MAIN_API_BASE_URL from `10.110.30.15:1250` to `[YOUR_IP]:5000` |
| 404 errors | Ensure `app/routes/machine_events.py` exists and is registered |
| Network unreachable | Check Raspberry Pi IP with `hostname -I` and update database |

---

## ✅ After Using These Guides

You should have:

✅ Working Raspberry Pi to Flask communication  
✅ Events recorded in database  
✅ Machine status visible on dashboard  
✅ Real-time monitoring of all machines  
✅ Complete troubleshooting knowledge for future issues  

---

## 💡 Key Files Modified/Created

**Code**:
- `app/routes/machine_events.py` - API endpoints (already created)
- `app/models/__init__.py` - Models (MachineStatus, MachineEvent added)
- `raspberrycode.py` - Needs URL update (line 44)

**Tools Created**:
- `diagnose_rpi_issues.py` - Auto diagnosis
- `check_events_quick.py` - Quick event check
- `query_machine_events.py` - Interactive query

**Documentation** (new):
- `TROUBLESHOOTING_MASTER_GUIDE.md` ← main reference
- `SYSTEM_INTEGRATION_FIX.md` ← step-by-step
- `RASPBERRY_CODE_CHANGES.md` ← code changes
- `FLASK_COMPONENTS_VERIFICATION.md` ← Flask setup check

---

## 🆘 Getting Help

If you're still stuck after following the guides:

1. **Run the diagnostic**: `python diagnose_rpi_issues.py`
2. **Check specifics**:
   ```bash
   # Verify Flask: python main.py (should run without errors)
   # Check database: mysql -u root -p (then: SELECT * FROM machines)
   # Test API: curl http://localhost:5000/api/events/machines/list
   ```
3. **Share output** from diagnostic tool - it will show exactly what's wrong

---

## 📝 Summary

You now have:

1. **Master Guide** - Complete overview of problem and solutions
2. **Step-by-Step Guide** - 10 detailed fix steps
3. **Code Changes Guide** - What to modify in Raspberry Pi code
4. **Flask Verification Guide** - Check Flask is set up correctly
5. **3 Automated Tools** - Diagnose and check status automatically

**Next Step**: Open `TROUBLESHOOTING_MASTER_GUIDE.md` and start with the "3-Minute Quick Fix" section!

Good luck! 🚀

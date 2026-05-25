# Preventive Maintenance Plan Card - Testing Guide

## ✅ System Status
- **Server**: Running on `http://localhost:5000`
- **Template**: `/app/templates/main/preventive_maintenance_plan_card.html`
- **Route**: `/preventive-maintenance-plan`
- **API Endpoint**: `/api/machines-by-zone/<zone_id>`

## 📊 Sample Data Available
- **Zones**: 
  - Cutting area (ID: 1)
  - Welding area (ID: 2)
  - Twisting area (ID: 3)
  - Assembly area (ID: 4)

- **Machines**: 
  - MACH001 - Komax (Cutting area)
  - MACH002 - Laser Cutter (Cutting area)
  - MACH003 - Press Machine (Cutting area)

## 🧪 Testing Steps

### Step 1: Open the Page
```
Open browser to: http://localhost:5000/preventive-maintenance-plan
(Make sure you are logged in first if required)
```

### Step 2: Test Zone Selection
1. Look for "Step 1: Select a Zone" section
2. Click the dropdown menu labeled "-- Choose a Zone --"
3. Select "Cutting area"
4. Watch the browser console (F12 → Console tab) for debug messages
5. Expected output: 
   - "Zone selected: 1"
   - "API response status: 200"
   - "Machines received: [{id, name, code}, ...]"

### Step 3: Test Machine Filtering
1. The "Step 2: Select a Machine" dropdown should now be enabled
2. It should show:
   - MACH001 - Komax
   - MACH002 - Laser Cutter
   - MACH003 - Press Machine
3. Select "MACH001 - Komax"
4. Console should show: "Machine selected: 1"

### Step 4: Verify Calendar Display
1. The "Step 3: Maintenance Schedule Calendar" section should appear
2. You should see 6 months of calendars side-by-side
3. Look for colored indicators:
   - 🔴 Red squares = 1-Month maintenance
   - 🟡 Yellow squares = 3-Month maintenance
   - 🔵 Blue squares = 6-Month maintenance

### Step 5: Check Schedule Details Table
1. Below the calendar, look for "Scheduled Maintenance Tasks" section
2. Verify the table shows:
   - Machine name: "MACH001 - Komax"
   - Three rows with frequencies: Monthly, Quarterly, Semi-Annual
   - Each with dates and task descriptions

## 🔍 Debugging Tips

### Open Browser Developer Tools
- Press `F12` or `Right-click → Inspect`
- Go to Console tab
- You should see messages like:
  - "Preventive Maintenance Plan Card - Script loaded successfully"
  - "Initializing event listeners..."
  - "✓ Zone select listener attached"
  - "✓ Machine select listener attached"

### Check for Errors
If anything doesn't work:
1. Look for red error messages in the console
2. Copy the error message
3. Check the Network tab (F12 → Network) for failed API calls
4. Verify the response from `/api/machines-by-zone/1` is valid JSON

### Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| Dropdowns not appearing | Ensure you're logged in as admin/supervisor/technician |
| Machines not loading after zone selection | Check console for API errors, verify `/api/machines-by-zone/<id>` works |
| Calendar not displaying | Check if machine selection triggered, look for JS errors in console |
| No colored schedule indicators | Verify calendar dates are within 7 months from today |

## 📋 Expected Workflow
```
1. Zone Selection ✓
   ↓
2. Machines Filter by Zone ✓
   ↓
3. Machine Selection ✓
   ↓
4. Calendar Display (6 months) ✓
   ↓
5. Schedule Details Table ✓
```

## 🚀 Quick Start
1. Open `http://localhost:5000/preventive-maintenance-plan` in browser
2. Login if required
3. Select "Cutting area" zone
4. Select "MACH001 - Komax" machine
5. View the 6-month calendar with maintenance schedules
6. See the schedule details table below

---

**Note**: All console logging is enabled for debugging. Check browser console (F12) for detailed execution flow.

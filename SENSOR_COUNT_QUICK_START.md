# Quick Start: Sensor Count Display

## ✅ Implementation Complete!

The sensor count display feature has been successfully added to your Maintenance System. Here's what was done:

## 📊 What's New?

### Machine Status Page Enhancement
Navigate to **`/machine-status`** to see:
- **Daily Count**: Impulses detected today per machine
- **Total Count**: Cumulative impulses since start
- **Threshold Progress**: Visual bar showing % to maintenance trigger
- **Status Alert**: Real-time indication of maintenance requirements
- **Auto-Updates**: Every 2 minutes (configurable)

## 🎯 Key Features

| Feature | Details |
|---------|---------|
| **API Endpoint** | `GET /api/sensor/display-counts/<machine_name>` |
| **Auto-Refresh** | Every 2 minutes (configurable) |
| **Visual Indicator** | Progress bar + color coding |
| **Status Alert** | Green (normal) / Yellow (maintenance due) |
| **Number Format** | Thousand separators for readability |
| **Update Animation** | Pulse effect when data refreshes |

## 📁 Files Modified

```
✅ app/routes/sensor_events.py
   └─ Added: sensor_display_counts() endpoint

✅ app/templates/machine_status_card_view.html
   ├─ Added: Sensor count display section
   ├─ Added: CSS styling for cards
   └─ Added: JavaScript auto-update logic

✅ SENSOR_COUNT_DISPLAY_GUIDE.md (NEW)
   └─ Complete implementation documentation

✅ test_sensor_display.py (NEW)
   └─ Testing utility script
```

## 🚀 How to Use

### 1. View Machine Status
```
Go to: /machine-status
You'll see sensor counts on each machine card
```

### 2. Test the API
```bash
# Option A: Using curl
curl http://localhost:5000/api/sensor/display-counts/MACHINE_001

# Option B: Using the test script
python test_sensor_display.py
```

### 3. Monitor in Browser
- Open **Machine Status** page
- Data updates automatically every 2 minutes
- Watch the progress bar move as impulses are detected
- Maintenance alert turns yellow when threshold is reached

## ⚙️ Configuration

### Change Auto-Refresh Interval
Edit `app/templates/machine_status_card_view.html` around line 250:

```javascript
// Default: 2 minutes
const REFRESH_INTERVAL = 2 * 60 * 1000;

// Examples:
// 1 minute:  1 * 60 * 1000
// 5 minutes: 5 * 60 * 1000
// 10 minutes: 10 * 60 * 1000
```

### Change Threshold Colors
Edit the same file, look for `progressBar.style.backgroundColor`:
- Normal: `#667eea` (blue)
- Alert: `#ffc107` (yellow)

## 📊 API Response Example

```json
{
    "machine_name": "MACHINE_001",
    "daily_count": 15234,
    "total_count": 285000,
    "threshold_value": 300000,
    "threshold_reached": false,
    "percentage_to_threshold": 95,
    "last_updated": "2026-05-18T10:30:45.123456"
}
```

## 🔧 Troubleshooting

### Data not updating?
1. Open browser DevTools (F12)
2. Check Console tab for errors
3. Verify machine has records in `sensor_counts` table
4. Confirm API endpoint responds: `/api/sensor/display-counts/<machine_name>`

### Numbers showing incorrectly?
1. Clear browser cache (Ctrl+Shift+Delete)
2. Refresh page (Ctrl+F5)
3. Check database `sensor_counts` table for data

### Colors not showing?
1. Ensure Bootstrap CSS is loaded
2. Check browser DevTools → Network tab
3. Verify no CSS conflicts

### Not seeing the display?
1. Check if machine is "active" in database
2. Verify sensor_counts table has records
3. Try accessing API directly to test

## 📈 Expected Behavior

| Scenario | Display |
|----------|---------|
| Normal Operation | Blue bar, green alert, updates every 2 min |
| Maintenance Due | Yellow bar, yellow alert, updates every 2 min |
| No Data | 0 counts, 0% progress, alert showing |
| Error | Console error, manual refresh available |

## 💡 Tips for Admin

1. **Monitor Regularly**: Check the dashboard every few hours
2. **Plan Maintenance**: When yellow alert appears, schedule maintenance
3. **Reset After Maintenance**: Reset counter when preventive maintenance is done
4. **Track Trends**: Watch how counts increase over time
5. **Adjust Interval**: Use smaller interval (1 min) during critical operations

## 📞 Support

For detailed information, see: `SENSOR_COUNT_DISPLAY_GUIDE.md`

For testing, use: `test_sensor_display.py`

## ✨ Summary

Your machine status page now provides:
- ✅ Real-time sensor count monitoring
- ✅ Visual threshold progress tracking
- ✅ Automatic maintenance alerts
- ✅ Auto-updating data (every 2 minutes)
- ✅ Professional dashboard display

All without requiring page refresh! Admin can monitor what's happening across all machines at a glance.

---

**Ready to Use**: Yes ✅
**Database Requirements**: sensor_counts table (already exists)
**Performance**: Minimal impact (light API calls + DOM updates)
**Browser Support**: All modern browsers (Chrome, Firefox, Safari, Edge)

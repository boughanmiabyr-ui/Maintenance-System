# Sensor Count Display Implementation Guide

## Overview
This feature adds real-time sensor count display to the Machine Status monitoring dashboard. Admins can see:
- **Daily Count**: Impulses detected today for each machine
- **Total Count**: Cumulative impulses since start
- **Threshold Progress**: Visual progress bar showing % to maintenance threshold
- **Maintenance Status**: Alert when preventive maintenance is due
- **Auto-Updates**: Refreshes every 2 minutes automatically

## Features Implemented

### 1. **New API Endpoint**
```
GET /api/sensor/display-counts/<machine_name>
```

**Response:**
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

### 2. **Machine Status View Updates**
- Location: `/machine-status`
- Each machine card now displays:
  - Daily sensor count
  - Total sensor count
  - Threshold progress bar (animated, with percentage)
  - Maintenance status (with color coding)
  - Last updated timestamp

### 3. **Auto-Refresh Functionality**
- **Interval**: Every 2 minutes (configurable)
- **Animation**: Pulse effect when data updates
- **Color Coding**:
  - Blue progress bar = Normal operation
  - Yellow progress bar = Maintenance due (threshold reached)
  - Green alert = Not due
  - Yellow alert = Maintenance due

### 4. **Display Features**
- **Thousand Separators**: Numbers formatted as "1,234,567" for readability
- **Progress Bar**: Shows percentage of threshold reached
- **Status Alerts**: Visual indication of maintenance requirements
- **Time Display**: Shows when data was last updated

## File Changes

### Modified Files:

1. **`app/routes/sensor_events.py`**
   - Added new endpoint: `sensor_display_counts()`
   - Line: ~135-180

2. **`app/templates/machine_status_card_view.html`**
   - Added sensor count display section
   - Added CSS styling for sensor cards
   - Added JavaScript for auto-refresh and updates
   - Total additions: ~150 lines

### New API Routes:
- `GET /api/sensor/display-counts/<machine_name>` - Get current sensor counts

## How to Use

### For Admins:
1. Navigate to **Machine Status Monitor** page (`/machine-status`)
2. Each machine card shows:
   - Current daily sensor count
   - Total cumulative count
   - Progress towards maintenance threshold
   - Maintenance due status
3. Data automatically updates every 2 minutes
4. If a machine reaches threshold:
   - Progress bar turns yellow
   - Alert changes to red/warning
   - Text shows "Preventive Maintenance Due!"

### For Integration:
The API endpoint can be called directly:
```bash
curl "http://localhost:5000/api/sensor/display-counts/MACHINE_001"
```

## Configuration

### Adjust Auto-Refresh Interval:
Edit `machine_status_card_view.html` line ~250:
```javascript
const REFRESH_INTERVAL = 2 * 60 * 1000; // Change to desired milliseconds
```

**Common Intervals:**
- 1 minute: `1 * 60 * 1000`
- 2 minutes: `2 * 60 * 1000` (current)
- 5 minutes: `5 * 60 * 1000`

### Adjust Threshold Colors:
Edit the CSS colors in the same file:
- Normal color: `#667eea` (blue)
- Due color: `#ffc107` (yellow)

## Technical Details

### Data Flow:
```
Machine → SensorCount Table
         ↓
API Endpoint (/api/sensor/display-counts/<machine>)
         ↓
JavaScript Fetch (every 2 min)
         ↓
HTML Update with Formatted Display
```

### Performance Considerations:
- **Database**: Single query per machine per refresh
- **Frontend**: Minimal DOM updates (only changed values)
- **Network**: Small JSON payload (~300 bytes)
- **Interval Cleanup**: Intervals cleared on page unload

## Database Requirements

Ensure the `sensor_counts` table exists with these columns:
- `id` (Primary Key)
- `machine_id` (Foreign Key)
- `date` (Date)
- `daily_count` (Integer)
- `total_count` (Integer)
- `threshold_value` (Integer, default 300000)
- `threshold_reached` (Boolean)
- `updated_at` (DateTime)

## Troubleshooting

### Sensor counts not updating?
1. Check browser console for errors (F12)
2. Verify API endpoint: `GET /api/sensor/display-counts/<machine_name>`
3. Check database for sensor_counts records

### Numbers not formatting correctly?
- Check JavaScript `formatNumber()` function
- Ensure data is numeric (not string)

### Maintenance alert not showing?
- Verify `threshold_reached` value in database
- Check alert element ID: `maintenance-status-${machineId}`

### Colors not displaying?
- Clear browser cache (Ctrl+Shift+Delete)
- Check CSS in browser DevTools
- Verify Bootstrap is loaded

## Future Enhancements

Possible improvements:
1. Real-time WebSocket updates instead of polling
2. Historical chart display
3. Notification/Email alerts
4. Configurable threshold per machine
5. Bulk reset functionality
6. Export sensor data to CSV

## Support

For issues or questions:
1. Check JavaScript console (F12 → Console)
2. Check server logs
3. Verify database connectivity
4. Check API endpoint returns valid JSON

---

**Implementation Date**: May 18, 2026
**Version**: 1.0
**Status**: Active

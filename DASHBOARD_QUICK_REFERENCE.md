# Dashboard Integration - Quick Reference

## ✅ What Was Done

### 1. **Machine Status Card**
- Added to main dashboard as module card
- Added quick-nav summary card
- Full page view at `/machine-status`
- Shows all machines with real-time status
- Event modal with recent events history
- Color: Cyan (#06b6d4)

### 2. **Preventive Maintenance Reports Card**
- Added to main dashboard as module card
- Added quick-nav summary card
- Full page view at `/preventive-reports`
- Shows all maintenance reports
- Includes search and filter capabilities
- Shows task completion progress
- Color: Teal (#14b8a6)

### 3. **Dashboard Integration**
- Both cards appear on main dashboard
- Module cards in the card grid (clickable)
- Quick navigation cards above other dashboard content
- Consistent styling with existing cards
- Responsive grid layout

---

## 📍 Where to Find Things

### On Main Dashboard (`/dashboard`)

**Module Cards Section** (at top):
- Look for cyan icon with heartbeat = Machine Status Monitor
- Look for teal icon with clipboard = Preventive Maintenance Reports

**Quick Navigation Section** (above existing content):
- Machine Status Monitor card with "{{ stats.total_machines }} Machines" badge
- Preventive Maintenance Reports card

### Full Pages:
- Machine Status: `/machine-status`
- Preventive Reports: `/preventive-reports`

---

## 🎨 Styling Information

### Colors Used
- Machine Status: Cyan (#06b6d4) with heartbeat icon
- Preventive Reports: Teal (#14b8a6) with clipboard icon
- All cards have left border accent and hover effects

### Layout
- Card Grid: Responsive (4 columns large, 3 medium, 2 small)
- Full Pages: 3-column grid for content cards
- Mobile: Single column stack

---

## 📊 What Data is Displayed

### Machine Status Cards Show:
- ✓ Machine Code & Name
- ✓ Current Status (working, downtime, maintenance, break, offline)
- ✓ Department & Zone
- ✓ Status Start Time
- ✓ Daily Downtime Hours
- ✓ Event History (modal)

### Preventive Reports Cards Show:
- ✓ Machine Code & Name
- ✓ Status (pending, in_progress, completed)
- ✓ Assigned Technician
- ✓ Start & Completion Dates
- ✓ Task Progress Bar
- ✓ Last Updated Time
- ✓ Quick Actions (View/Continue)

---

## 🔗 API Endpoints Used

```
GET  /api/events/machines/list
GET  /api/events/machine_status/<machine_code>
GET  /api/events/recent/<machine_code>?hours=24
```

See `RASPBERRY_PI_INTEGRATION_GUIDE.md` for full API documentation.

---

## 🚀 Access & Permissions

**Who can see Machine Status?**
- Admin ✓
- Supervisor ✓
- Technician ✓
- Stock Agent ✗
- Other Roles ✗

**Who can see Preventive Reports?**
- Admin (all) ✓
- Supervisor (all) ✓
- Technician (own only) ✓
- Stock Agent ✗
- Other Roles ✗

---

## 📁 Files Reference

| File | Purpose |
|------|---------|
| `app/routes/main.py` | Dashboard & new routes |
| `app/templates/main/dashboard.html` | Main dashboard template |
| `app/templates/machine_status_card_view.html` | Machine status full page |
| `app/templates/preventive_reports_card_view.html` | Reports full page |
| `app/routes/machine_events.py` | API endpoints |
| `app/__init__.py` | Blueprint registration |

---

## 🧪 To Test the Integration

1. **Dashboard**: Navigate to `/dashboard`
   - You should see 2 new cards at top (if admin/supervisor/technician)
   - Plus 2 more full-width cards above other content

2. **Machine Status**: Click the Machine Status card or go to `/machine-status`
   - See all machines as cards
   - Click "View Events" on any machine to see event history

3. **Preventive Reports**: Click the Preventive Reports card or go to `/preventive-reports`
   - See all reports as cards
   - Use search/filter at top
   - Click "View Details" or "Continue Report"

4. **Module Access**: From dashboard, you can also click the module cards in the grid

---

## 📝 Database Tables Used

- `machines` - Machine information
- `machine_status` - Real-time status tracking
- `machine_events` - Event audit trail
- `preventive_maintenance_execution` - Report records
- `preventive_maintenance_task_execution` - Task completion

---

## 🐛 Troubleshooting

**Cards not showing?**
- Check user role (must be admin, supervisor, or technician)
- Verify database has active machines
- Check browser console for JavaScript errors

**Events not appearing?**
- Verify Raspberry Pi is sending events to API
- Check machine code matches exactly
- Look at API logs for errors

**Data not updating?**
- Machine Status cards refresh every 30 seconds on full page
- Dashboard cards show snapshot at page load
- Refresh page to get latest data

---

## 📚 Additional Documentation

- Full Raspberry Pi integration: `RASPBERRY_PI_INTEGRATION_GUIDE.md`
- API tester tool: `api_tester.html`
- Database schema: Check models in `app/models/__init__.py`

---

**Last Updated**: March 16, 2026
**Dashboard Status**: ✅ Fully Integrated

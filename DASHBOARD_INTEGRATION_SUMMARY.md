# Dashboard Integration Summary

## Overview
All machine status monitoring and preventive maintenance reports have been fully integrated into the main dashboard as proper cards, following the same design pattern as other dashboard modules.

## Dashboard Structure

### 1. Module Cards (Grid View)
Located at the top of the dashboard, the following new module cards have been added:
- **Machine Status Monitor** (Color: Cyan #06b6d4)
  - Icon: heartbeat
  - Description: Real-time machine status and events
  - Accessible to: admin, supervisor, technician

- **Preventive Maintenance Reports** (Color: Teal #14b8a6)
  - Icon: clipboard-list
  - Description: View preventive maintenance execution reports
  - Accessible to: admin, supervisor, technician

### 2. Quick Navigation Cards (Below Module Grid)
Two new full-width cards for quick navigation:

#### Machine Status Monitor Card
- Shows total active machines count as a badge
- Highlighted with left border (cyan #06b6d4)
- Hover effect: lifts slightly above dashboard
- Directs to: `/machine-status` (full page view)

#### Preventive Maintenance Reports Card
- Provides quick access to all maintenance reports
- Highlighted with left border (teal #14b8a6)
- Hover effect: lifts slightly above dashboard
- Directs to: `/preventive-reports` (full page view)

### 3. Dashboard Flow

```
Main Dashboard (/)
├── Module Cards Grid
│   ├── Stock Management
│   ├── Preventive Maintenance Plan
│   ├── Spare Parts Demands
│   ├── Machine Status Monitor ← NEW
│   └── Preventive Maintenance Reports ← NEW
│
├── Quick Navigation Cards (Full Width)
│   ├── Machine Status Monitor Summary ← NEW
│   └── Preventive Maintenance Reports Summary ← NEW
│
├── Admin Analytics Card (Admin only)
│
├── Maintenance Report Widget
│
└── Other Dashboard Content
```

## Full Page Views

### Machine Status Card View (`/machine-status`)
**URL**: `/machine-status`
**Layout**: Grid (3 columns on large screens)
**Features**:
- Shows all active machines as individual cards
- Current status with color-coded badge
- Department and zone information
- Time status started
- Daily downtime total
- "View Events" button shows recent machine events in modal
- Modal displays:
  - Event type
  - Start time
  - Duration (auto-calculated)
  - Status (ended/active/cancelled)

### Preventive Reports Card View (`/preventive-reports`)
**URL**: `/preventive-reports`
**Layout**: Grid (3 columns on large screens)
**Features**:
- Shows all preventive maintenance executions as cards
- Search by machine code or technician name
- Filter by status (pending, in_progress, completed)
- Task completion progress bar
- Machine information and assigned technician
- Start and completion dates
- Status badge with color coding
- "View Details" button - links to detailed report
- "Continue Report" button - (if not completed) links to continue filling the report
- Last updated timestamp

## Styling & Colors

### Color Scheme
| Component | Color | Hex |
|-----------|-------|-----|
| Machine Status | Cyan | #06b6d4 |
| Preventive Reports | Teal | #14b8a6 |
| Stock | Blue | #3b82f6 |
| Maintenance | Green | #10b981 |
| Spare Parts | Amber | #f59e0b |

### Card Styling
- Consistent rounded corners (0.5rem)
- Subtle drop shadows
- Left border accent (5px)
- Hover effects (lift up slightly with enhanced shadow)
- Responsive grid layout

## Data Structure

### Machine Status Card Shows
- Machine Code
- Machine Name
- Department
- Zone
- Current Status (working, downtime, maintenance, break, offline)
- Status Start Time
- Cumulative Downtime Today

### Preventive Reports Card Shows
- Machine Code & Name
- Status (pending, in_progress, completed)
- Assigned Technician
- Start Date
- Completed Date (if applicable)
- Task Progress (completed/total)
- Recent Update Timestamp

## API Integration

All data is fetched from:
1. **Database Models**:
   - `Machine` - machine information
   - `MachineStatus` - current machine status
   - `PreventiveMaintenanceExecution` - execution records

2. **API Endpoints** (for machine events):
   - `GET /api/events/machines/list` - list all machines
   - `GET /api/events/machine_status/<machine_code>` - get current status
   - `GET /api/events/recent/<machine_code>` - get recent events

## Dashboard Route Updates

### Updated Dashboard Function
File: `app/routes/main.py` - `dashboard()` function

**New Modules Added**:
```python
'machine_status': {
    'title': 'Machine Status Monitor',
    'icon': 'heartbeat',
    'description': 'Real-time machine status and events',
    'url': 'main.machine_status_view',
    'roles': ['admin', 'supervisor', 'technician'],
    'color': '#06b6d4'
},
'preventive_reports': {
    'title': 'Preventive Maintenance Reports',
    'icon': 'clipboard-list',
    'description': 'View preventive maintenance execution reports',
    'url': 'main.preventive_reports_view',
    'roles': ['admin', 'supervisor', 'technician'],
    'color': '#14b8a6'
}
```

**New Statistics Tracked**:
```python
stats = {
    ...existing stats...,
    'pending_executions': <count>,
    'in_progress_executions': <count>
}
```

## New Routes Added

### Route 1: Machine Status View
```python
@main_bp.route('/machine-status')
@login_required
@role_required('admin', 'supervisor', 'technician')
def machine_status_view():
    # Full page view with all machines and their status
    # Displays event history with modal
```

### Route 2: Preventive Reports View
```python
@main_bp.route('/preventive-reports')
@login_required
@role_required('admin', 'supervisor', 'technician')
def preventive_reports_view():
    # Full page view with all preventive maintenance reports
    # Includes filtering and search functionality
```

## User Experience Flow

### For Admin/Supervisor:
1. Opens Dashboard → Sees all available modules including new ones
2. Can click Machine Status module card or quick nav card
3. Views all machines with real-time status
4. Can expand individual machines to see event history
5. Can click Preventive Reports card
6. Views all maintenance reports with search/filter
7. Can continue or view details of any report

### For Technician:
1. Opens Dashboard → Sees machines and reports they have access to
2. Can view their assigned machine status
3. Can view their assigned preventive maintenance reports
4. Can continue filling reports they're assigned to

## Files Modified

1. **app/routes/main.py**
   - Added new modules for dashboard cards
   - Added new route: `machine_status_view()`
   - Added new route: `preventive_reports_view()`
   - Updated dashboard statistics

2. **app/templates/main/dashboard.html**
   - Added Machine Status Monitor quick nav card
   - Added Preventive Reports quick nav card

3. **app/__init__.py**
   - Registered events_bp blueprint (for API endpoints)

4. **app/rules/machine_events.py** (Created)
   - All API endpoints for machine event handling

## Template Files Created

1. **machine_status_card_view.html** - Full page grid view
2. **preventive_reports_card_view.html** - Full page grid with filters
3. **machine_status_widget.html** - Dashboard widget (optional, for inline display)

## Summary

The dashboard now provides:
✅ Integrated Machine Status Monitoring
✅ Integrated Preventive Reports Management
✅ Consistent Card-Based UI
✅ Role-Based Access Control
✅ Real-Time Status Display
✅ Search and Filter Capabilities
✅ Event History Tracking
✅ Task Progress Visualization
✅ Mobile-Responsive Design
✅ Intuitive Navigation

All components follow the existing dashboard design patterns and are fully integrated into the main application workflow.

# Preventive Maintenance Report - Duration Tracking Improvements

## Overview
The preventive maintenance report now features **persistent, server-side duration tracking** that allows you to:
- ✅ Stay on the same page while tasks run
- ✅ Create and save reports automatically
- ✅ Track duration even if you navigate away
- ✅ Return to the report and see updated progress
- ✅ Automatically calculate elapsed time from the database

## Key Features

### 1. **Real-Time Server-Side Duration Tracking**
- Duration is calculated from the database (`start_time` to current time)
- Works even if you reload the page or navigate away
- The timer continues tracking on the server side
- No data loss if browser crashes or closes

### 2. **Stay on Same Page**
- When you click "Start" on a task, it stays on the execution report page
- No page redirects occur
- You can manage multiple tasks without leaving the page

### 3. **Refresh Button**
- Located at the top-right of the execution report (next to status badges)
- Click the **Refresh** button to update all task durations from the server
- Useful after navigating away and coming back
- Shows "Refreshing..." state while updating

### 4. **Continuous Duration Updates**
- Each task's duration updates automatically every second
- Duration is fetched from the server for accuracy
- Changes reflect in real-time on the table

## How It Works

### Backend (API Endpoints)

**New Endpoint: `GET /preventive-maintenance/task-execution/<task_id>/duration`**
- Returns current elapsed duration for a running task
- Calculates time server-side: `now - start_time`
- Returns duration in both seconds and minutes
- Works for pending, in_progress, and completed tasks

```json
{
  "success": true,
  "status": "in_progress",
  "elapsed_seconds": 125,
  "elapsed_minutes": 2,
  "start_time": "2026-03-17T10:30:00.000000"
}
```

### Frontend (JavaScript)

**Key Functions:**

1. **`updateTaskDurationFromServer(taskId)`**
   - Fetches latest duration from server
   - Updates display with minutes and seconds
   - Called every second for tasks in progress

2. **`startTaskTimer(taskId, startTime)`**
   - Sets up periodic refresh of duration from server
   - Replaces the old client-side timer
   - Ensures accuracy across page navigations

3. **`refreshAllTaskDurations()`**
   - Manual refresh of all task durations
   - Called when user clicks "Refresh" button
   - Useful after returning to the page

## Usage Workflow

### Starting a Task
1. Click the **Start** button on a task row
2. Task status changes to "IN PROGRESS" with yellow highlight
3. Duration timer starts, updating every second from the server
4. You remain on the execution report page

### Navigating Away
1. You can click other links or navigate to different pages
2. The task continues running on the server
3. Database records the `start_time` and tracks progress

### Returning to the Report
1. Go back to the preventive maintenance execution report
2. Click the **Refresh** button at the top-right
3. All task durations update with current elapsed times
4. You'll see where each task is at in its execution

### Stopping a Task
1. Click the **End** button on the running task
2. Modal dialog opens asking for task details
3. Fill in findings, actions, issues, etc.
4. Click "Complete Task"
5. Task duration is recorded and frozen
6. Status changes to "COMPLETED" with green badge

## Database Changes
None required! The system uses existing database columns:
- `PreventiveMaintenanceTaskExecution.start_time` - When task started
- `PreventiveMaintenanceTaskExecution.end_time` - When task ended
- `PreventiveMaintenanceTaskExecution.actual_duration_minutes` - Calculated duration

## Technical Details

### How Duration is Calculated

**For In-Progress Tasks:**
```python
elapsed_time = datetime.utcnow() - task_exec.start_time
elapsed_seconds = int(elapsed_time.total_seconds())
```

**For Completed Tasks:**
```python
actual_duration = task_exec.end_time - task_exec.start_time
duration_minutes = int(actual_duration.total_seconds() / 60)
```

### Frontend Update Cycle
```
Every 1 second:
  1. Fetch duration from /duration endpoint
  2. Update display with MM:SS format
  3. Continue until task is completed
```

## Browser Compatibility
- Works on all modern browsers (Chrome, Firefox, Edge, Safari)
- Uses standard Fetch API for AJAX requests
- No special plugins or extensions required

## Benefits

| Feature | Before | After |
|---------|--------|-------|
| Page stays same | ❌ Required reload | ✅ No reload needed |
| Track after navigation | ❌ Timer resets | ✅ Server continues tracking |
| Duration persistence | ❌ Lost on refresh | ✅ Always in database |
| Real-time updates | ⚠️ Client-side only | ✅ Server-side accurate |
| Coming back to report | ❌ Manual retiming | ✅ Auto-updates |

## Future Enhancements
- Auto-refresh intervals (refresh durations every 5-10 seconds)
- Duration history chart showing task time trends
- Pause/Resume task capability
- Task duration warnings (when exceeding estimated time)
- Comparison with estimated vs actual duration

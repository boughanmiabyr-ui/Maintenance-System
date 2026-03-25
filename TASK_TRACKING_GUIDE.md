# Preventive Maintenance Task Tracking System

## Overview

The maintenance system now includes a comprehensive **task-level tracking** feature that allows technicians to manually start and end each preventive maintenance task, with automatic time tracking and detailed reporting.

## Key Features

✅ **22 French Maintenance Tasks** - Complete checklist for preventive maintenance
✅ **Manual Start/End Tracking** - Technicians control when each task begins and ends
✅ **Automatic Time Calculation** - System tracks elapsed time between start and end
✅ **Real-time Timer Display** - Visual timer shows time spent on current task
✅ **Detailed Task Reporting** - Capture findings, actions, issues, materials, and quality checks
✅ **Task Status Tracking** - Status: Pending → In Progress → Completed (or Skipped)
✅ **Database Persistence** - All data is stored in the database for reporting and analysis
✅ **Progress Visualization** - Overall completion percentage shown in progress bar

## Database Schema

### Tables Involved

#### `preventive_maintenance_tasks`
Stores the template tasks for a maintenance plan.

```sql
- id: Primary key
- plan_id: Foreign key to maintenance plan
- task_number: Sequence number (1-22)
- task_description: French description of the task
- category: Category (Safety, Mechanical, Electrical, etc.)
- estimated_duration_minutes: Initial estimate
- required_materials: List of required materials
- safety_precautions: Safety information
- notes: Additional notes
```

#### `preventive_maintenance_task_executions`
Tracks the execution of individual tasks.

```sql
- id: Primary key
- execution_id: Foreign key to maintenance execution
- task_id: Foreign key to task template
- technician_id: Who performed the task
- order_number: Task sequence
- status: pending | in_progress | completed | skipped | unable_to_complete
- start_time: TIMESTAMP when task started
- end_time: TIMESTAMP when task ended
- actual_duration_minutes: Calculated duration (end_time - start_time)
- findings: What was found/observed
- actions_taken: What was done
- issues_encountered: Any problems encountered
- materials_used: Materials/parts used
- completion_notes: Additional notes
- quality_check: passed | failed | not_applicable
- quality_notes: Quality check observations
```

## How It Works

### 1. Create a Maintenance Plan with Tasks

Run the seed script to create the 22-task French maintenance plan:

```bash
python seed_preventive_maintenance_tasks.py
```

This creates:
- A maintenance plan: "Plan de Maintenance Préventive Complet (22 Tâches)"
- 22 tasks with French descriptions and categories
- Associations to the machine

### 2. Schedule a Maintenance Execution

As an admin/supervisor:
1. Go to **Preventive Maintenance** → **Plans**
2. Click on the plan
3. Click **Schedule Execution**
4. Select technician and date
5. System automatically creates task execution records (one per task)

### 3. Technician Performs Maintenance

As a technician:
1. View assigned execution in **Preventive Maintenance** → **Executions**
2. Click on execution to see all 22 tasks
3. For each task:

#### Task Workflow:

**Initial State:** `PENDING`
- Shows "Start" button
- Task is not yet active

**Starting a Task:** Click "Start"
- Status changes to `IN_PROGRESS` 
- Start time is recorded (current timestamp)
- Timer appears showing elapsed time
- "End" and "Skip" buttons replace "Start"

**Real-time Tracking:**
- Timer updates every second showing: `Xm YYs`
- Row highlights in yellow to show active task

**Completing a Task:** Click "End"
- Modal popup appears with form fields
- Timer shows final elapsed time (read-only)
- Fill in task details:
  - **Findings**: What you observed
  - **Actions Taken**: What you did to fix/maintain
  - **Issues Encountered**: Any problems
  - **Materials Used**: Tools, parts, materials used
  - **Additional Notes**: Any other observations
  - **Quality Check**: Passed / Failed / Not Applicable

- Click "Complete Task"
- End time is recorded
- Actual duration is calculated automatically
- Task status changes to `COMPLETED`
- Row highlights in green
- "View" button now available

**Skipping a Task:** Click "Skip"
- Modal appears asking reason
- Task status changes to `SKIPPED`
- No timing data is recorded
- Reason is stored in completion_notes

### 4. View Task Executions

Click "View" on completed tasks to see:
- Full task description
- Estimated vs actual duration
- Quality check result
- All recorded findings and actions

### 5. Submit for Approval

Once all tasks are completed:
1. Scroll to **Complete Execution** section
2. Provide overall findings and machine condition
3. Indicate if issues found and spare parts needed
4. Click **Submit for Approval**
5. System calculates:
   - Total duration (sum of all task durations)
   - Completion percentage
   - Next scheduled maintenance date

### 6. Supervisor Approval

Supervisor reviews:
- All task details and durations
- Quality checks
- Any issues or recommendations
- Approves or rejects the execution

## The 22 French Maintenance Tasks

| # | Task | Category | Est. Time |
|---|------|----------|-----------|
| 1 | Verify safety system (emergency stop, controls) | Safety | 15 min |
| 2 | Check workstation accessories (magnifier, ruler, light) | Accessories | 10 min |
| 3 | Purge water from conditioning unit | Hydraulic | 20 min |
| 4 | Check insulation of cable sheaths | Electrical | 10 min |
| 5 | Check bearing mobility and noise | Mechanical | 15 min |
| 6 | Inspect belt, gear, and bearing wear | Mechanical | 20 min |
| 7 | Clean welding wheel with copper brush | Mechanical | 25 min |
| 8 | Check gripper pincer mobility | Mechanical | 15 min |
| 9 | Inspect blade wear | Mechanical | 20 min |
| 10 | Check conveyor belt tension (0.35mm tolerance) | Mechanical | 20 min |
| 11 | verify electrical cabinet fan operation | Electrical | 10 min |
| 12 | Position straightening arms to zero | Mechanical | 25 min |
| 13 | Check pressure gauges (Main: 6-8, Drive: 1.5-2.5, Press: 4-8 bar) | Hydraulic | 15 min |
| 14 | Verify press calibration with calibration tool | Mechanical | 30 min |
| 15 | Verify TOP WIN parameters (wire tolerance, strip length, etc.) | Electrical | 20 min |
| 16 | Verify only dry compressed air is used | Pneumatic | 15 min |
| 17 | Check straightening unit movement | Mechanical | 15 min |
| 18 | Verify straightening unit alignment | Mechanical | 20 min |
| 19 | Check arm movement | Mechanical | 15 min |
| 20 | Check tool gripping claws for wear/tightness | Mechanical | 20 min |
| 21 | Verify product length and tolerance (2000mm ±4mm) | Quality | 25 min |
| 22 | Document and sign maintenance report | Administrative | 15 min |

**Total Estimated Time: 352 minutes ≈ 5 hours 52 minutes**

## API Endpoints

```
POST /preventive-maintenance/task-execution/<task_exec_id>/start
- Starts a task, records start_time
- Returns: { success: bool, message: str, start_time: ISO timestamp }

POST /preventive-maintenance/task-execution/<task_exec_id>/end
- Completes a task with details
- Body: { findings, actions_taken, issues_encountered, materials_used, completion_notes, quality_check }
- Returns: { success: bool, message: str, end_time: ISO timestamp, duration_minutes: int }

POST /preventive-maintenance/task-execution/<task_exec_id>/skip
- Skips a task
- Body: { reason: str }
- Returns: { success: bool, message: str }
```

## Database Queries

### Get All Task Executions for an Execution
```sql
SELECT * FROM preventive_maintenance_task_executions
WHERE execution_id = ? 
ORDER BY order_number;
```

### Get Task Duration Statistics
```sql
SELECT 
    task_id,
    COUNT(*) as times_executed,
    AVG(actual_duration_minutes) as avg_duration,
    MIN(actual_duration_minutes) as min_duration,
    MAX(actual_duration_minutes) as max_duration
FROM preventive_maintenance_task_executions
WHERE status = 'completed'
GROUP BY task_id;
```

### Get Technician Performance
```sql
SELECT 
    technician_id,
    COUNT(*) as tasks_completed,
    AVG(actual_duration_minutes) as avg_task_duration,
    SUM(actual_duration_minutes) as total_maintenance_time
FROM preventive_maintenance_task_executions
WHERE status = 'completed'
GROUP BY technician_id;
```

## Usage Example

1. **Setup:** `python seed_preventive_maintenance_tasks.py`
2. **Create Execution:** Admin → Schedule new execution
3. **Execute:** Technician clicks Start/End for each task
4. **Track:** Real-time timer shows task duration
5. **Report:** Submit when all tasks done
6. **Approve:** Supervisor reviews and approves

## Status Values

| Status | Description |
|--------|-------------|
| `pending` | Task not yet started |
| `in_progress` | Task currently being performed |
| `completed` | Task finished with data |
| `skipped` | Task was skipped (reason recorded) |
| `unable_to_complete` | Task could not be completed (reason recorded) |

## Quality Check Values

| Value | Meaning |
|-------|---------|
| `passed` | Task quality check passed |
| `failed` | Task failed quality check |
| `not_applicable` | Quality check not applicable for this task |

## Execution Statuses

| Status | Description |
|--------|-------------|
| `scheduled` | Execution scheduled but not started |
| `started` | At least one task has been started |
| `completed` | All tasks completed/skipped |
| `cancelled` | Execution was cancelled |

## Report Status

| Status | Description |
|--------|-------------|
| `draft` | No tasks completed yet |
| `submitted` | Technician submitted for approval |
| `approved` | Supervisor approved |
| `rejected` | Supervisor rejected, reset to scheduled |

## Tips & Best Practices

✅ Plan time allocation based on task complexity
✅ Always document findings, even if task is skipped
✅ Take photos during maintenance for reference
✅ Record any deviations from estimated time
✅ Quality checks help identify recurring issues
✅ Use notes for communication with supervisor
✅ Complete all tasks before submitting
✅ Review supervisor feedback for next execution

## Troubleshooting

**Timer not showing?**
- Ensure JavaScript is enabled in browser
- Refresh page if needed
- Check browser console for errors

**Duration showing 0?**
- Make sure both start_time and end_time are recorded
- Duration is calculated as: end_time - start_time

**Cannot start new task?**
- Check if previous task is completed/skipped
- Verify you have edit permissions

**Data not saving?**
- Check database connection
- Verify user permissions
- Check server logs for errors

## Future Enhancements

- [ ] Task templates with auto-task creation
- [ ] Recurring maintenance plans
- [ ] KPI dashboards for maintenance metrics
- [ ] Mobile app integration
- [ ] Predictive maintenance based on history
- [ ] Integration with work order system
- [ ] Automated alerts for time overruns
- [ ] Maintenance cost tracking

---

**Version:** 1.0
**Last Updated:** March 2026
**Maintainer:** Maintenance System Team

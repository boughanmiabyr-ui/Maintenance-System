# Quick Start Guide: Preventive Maintenance Task Tracking

## 🚀 Quick Setup (5 minutes)

### Step 1: Verify Database Schema
Run the verification script to ensure all tables exist:
```bash
mysql -u root -p maintenance_system_v2 < TASK_TRACKING_VERIFICATION.sql
```

### Step 2: Populate the 22 French Maintenance Tasks
In your Python environment:
```bash
cd c:\Users\Arij Arouja\Desktop\appstage2026PFE-main
python seed_preventive_maintenance_tasks.py
```

Expected output:
```
======================================================================
French Preventive Maintenance Plan Seeder
======================================================================

✓ Created maintenance plan: 'Plan de Maintenance Préventive Complet (22 Tâches)' (ID: X)
  Machine: [Machine Name] ([Machine Code])
  Frequency: monthly (30 days)

Adding 22 maintenance tasks...
  Task  1: Vérifier le système de sécurité de la machine (15 min)
  Task  2: Vérifier l'état des accessoires liés au poste de travail (10 min)
  ...
  Task 22: Documentation et signature du rapport de maintenance (15 min)

✓ Successfully created 22 maintenance tasks
✓ Total estimated maintenance time: 352 minutes (5h 52m)

✓ Seeding completed successfully!
✓ You can now schedule executions for maintenance plan ID: X
```

### Step 3: Access the Web Interface
1. Start the Flask app: `python main.py`
2. Login as supervisor/admin
3. Navigate to **Preventive Maintenance** → **Plans**
4. Find "Plan de Maintenance Préventive Complet (22 Tâches)"
5. Click on it and review the 22 tasks

### Step 4: Schedule Your First Execution
1. Click **Schedule Execution**
2. Select:
   - Technician: [Your technician]
   - Supervisor: [You]
   - Scheduled Date: Today or tomorrow
3. Click **Schedule**
4. System automatically creates task records

### Step 5: Execute as Technician
1. Login as technician
2. Go to **Preventive Maintenance** → **Executions**
3. Find your scheduled execution
4. Click on it to see all 22 tasks

## 🎯 Step-by-Step Task Execution

### For Each Task:

1. **View task details**
   - Task number, description, category
   - Estimated duration
   - Requirements and safety precautions

2. **Start the task**
   - Click **Start** button
   - System records start time
   - Task status: `IN_PROGRESS`
   - Timer appears: `0m 00s`

3. **Perform the task**
   - Follow safety precautions
   - Observe findings
   - Record actions taken
   - Timer continues updating

4. **Complete the task**
   - Click **End** button
   - Modal form appears
   - Fill in observations:
     - ✓ Findings (what you saw)
     - ✓ Actions taken (what you did)
     - ✓ Issues encountered
     - ✓ Materials used
     - ✓ Quality check result
   - Click **Complete Task**
   - Task status: `COMPLETED` ✓
   - Time automatically calculated

5. **Or skip the task**
   - Click **Skip** if task not needed
   - Enter reason
   - Task status: `SKIPPED`

## 📊 Progress Tracking

- **Progress Bar**: Shows % of tasks completed in real-time
- **Completed Count**: Badge shows "[X] Completed" in header
- **Task Status**:
  - ⚪ Pending (gray) - Not started
  - 🟡 In Progress (yellow) - Currently working
  - 🟢 Completed (green) - Done
  - ⚫ Skipped (dark) - Skipped

## 📋 Task Categories

The 22 tasks are organized by category:

| Category | Tasks | Time |
|----------|-------|------|
| Safety | 1 | 15 min |
| Accessories | 2 | 10 min |
| Hydraulic | 3, 13 | 35 min |
| Electrical | 4, 11, 15 | 45 min |
| Mechanical | 5-10, 12, 14, 17-20 | 230 min |
| Pneumatic | 16 | 15 min |
| Quality | 21 | 25 min |
| Administrative | 22 | 15 min |

## 💾 Data That Gets Recorded

For each task execution, the system stores:

```
- start_time: 2026-03-12 09:30:00
- end_time: 2026-03-12 09:45:00
- actual_duration_minutes: 15
- findings: "Emergency stop button working correctly"
- actions_taken: "Tested all emergency stops"
- issues_encountered: "None found"
- materials_used: "Testing equipment"
- completion_notes: "All safety systems operational"
- quality_check: "passed"
- quality_notes: "All systems meet requirements"
```

## 🔍 Viewing Results

### As Technician:
- View all completed tasks with details
- See actual time vs estimated time
- Review quality checks

### As Supervisor:
- See technician performance
- Review all findings and issues
- Approve or request changes
- Generate reports

### Analytics Available:
- Average time per task
- Task completion rates
- Quality check statistics
- Technician performance metrics
- Trend analysis

## 🛠️ Common Tasks

### Check Plan Tasks
```sql
SELECT * FROM preventive_maintenance_tasks 
WHERE plan_id = 1 
ORDER BY task_number;
```

### View Execution Progress
```sql
SELECT 
  SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
  COUNT(*) as total
FROM preventive_maintenance_task_executions 
WHERE execution_id = 123;
```

### Get Technician Stats
```sql
SELECT 
  username,
  COUNT(*) as tasks_completed,
  ROUND(AVG(actual_duration_minutes), 1) as avg_time
FROM preventive_maintenance_task_executions te
JOIN users u ON te.technician_id = u.id
WHERE te.status = 'completed'
GROUP BY u.id;
```

## 📱 Mobile Considerations

The UI is responsive and works on:
- Desktop browsers (Chrome, Firefox, Edge)
- Tablets (iPad, Android tablets)
- Mobile phones (for viewing only, best on tablets for input)

## ⚙️ Configuration

### To Adjust Initial Settings:
Edit [plan_detail.html](app/templates/preventive_maintenance/plan_detail.html):
- Changed estimated durations
- Added/removed categories
- Modify task descriptions

### To Add More Tasks:
1. Edit `seed_preventive_maintenance_tasks.py`
2. Add new task to `MAINTENANCE_TASKS` list
3. Re-run: `python seed_preventive_maintenance_tasks.py`

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Timer not showing | Refresh browser, check JavaScript console |
| Data not saving | Check database connection, verify user permissions |
| Can't start task | Previous task might not be completed/skipped |
| Duration shows 0 | Ensure both start and end times recorded |
| Tasks not listed | Run seed script to create tasks |

## 📞 Support

For issues or questions:
1. Check [TASK_TRACKING_GUIDE.md](TASK_TRACKING_GUIDE.md) for detailed info
2. Run verification: `mysql < TASK_TRACKING_VERIFICATION.sql`
3. Check server logs: `debug.log` or console output
4. Contact system administrator

## 📈 Next Steps

After setup:
1. ✅ Test with one execution
2. ✅ Train technicians on process
3. ✅ Review first execution with supervisor
4. ✅ Adjust task details based on feedback
5. ✅ Start using for daily/monthly maintenance
6. ✅ Generate reports and analyze trends

---

**Ready to go!** Start with Step 1 above.

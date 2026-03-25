-- Database Verification Script for Preventive Maintenance Task Tracking
-- This script verifies that all necessary tables exist with proper schema

-- ============================================
-- 1. VERIFY PREVENTIVE_MAINTENANCE_PLANS TABLE
-- ============================================
SELECT 
    COLUMN_NAME, 
    COLUMN_TYPE, 
    IS_NULLABLE, 
    COLUMN_KEY,
    EXTRA
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = DATABASE() 
  AND TABLE_NAME = 'preventive_maintenance_plans'
ORDER BY ORDINAL_POSITION;

-- ============================================
-- 2. VERIFY PREVENTIVE_MAINTENANCE_TASKS TABLE
-- ============================================
SELECT 
    COLUMN_NAME, 
    COLUMN_TYPE, 
    IS_NULLABLE, 
    COLUMN_KEY,
    EXTRA
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = DATABASE() 
  AND TABLE_NAME = 'preventive_maintenance_tasks'
ORDER BY ORDINAL_POSITION;

-- ============================================
-- 3. VERIFY PREVENTIVE_MAINTENANCE_EXECUTIONS TABLE
-- ============================================
SELECT 
    COLUMN_NAME, 
    COLUMN_TYPE, 
    IS_NULLABLE, 
    COLUMN_KEY,
    EXTRA
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = DATABASE() 
  AND TABLE_NAME = 'preventive_maintenance_executions'
ORDER BY ORDINAL_POSITION;

-- ============================================
-- 4. VERIFY PREVENTIVE_MAINTENANCE_TASK_EXECUTIONS TABLE (KEY TABLE FOR TRACKING)
-- ============================================
SELECT 
    COLUMN_NAME, 
    COLUMN_TYPE, 
    IS_NULLABLE, 
    COLUMN_KEY,
    EXTRA
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = DATABASE() 
  AND TABLE_NAME = 'preventive_maintenance_task_executions'
ORDER BY ORDINAL_POSITION;

-- ============================================
-- 5. COUNT RECORDS IN EACH TABLE
-- ============================================
SELECT 
    (SELECT COUNT(*) FROM preventive_maintenance_plans) as total_plans,
    (SELECT COUNT(*) FROM preventive_maintenance_tasks) as total_tasks,
    (SELECT COUNT(*) FROM preventive_maintenance_executions) as total_executions,
    (SELECT COUNT(*) FROM preventive_maintenance_task_executions) as total_task_executions;

-- ============================================
-- 6. LIST PREVENTIVE MAINTENANCE PLANS WITH TASK COUNT
-- ============================================
SELECT 
    p.id,
    p.plan_name,
    m.name as machine_name,
    p.frequency_type,
    p.is_active,
    COUNT(t.id) as task_count,
    SUM(t.estimated_duration_minutes) as total_estimated_minutes
FROM preventive_maintenance_plans p
LEFT JOIN machines m ON p.machine_id = m.id
LEFT JOIN preventive_maintenance_tasks t ON p.id = t.plan_id
GROUP BY p.id, p.plan_name, m.name, p.frequency_type, p.is_active;

-- ============================================
-- 7. LIST TASKS FOR EACH PLAN
-- ============================================
SELECT 
    p.plan_name,
    t.task_number,
    t.task_description,
    t.category,
    t.estimated_duration_minutes,
    COUNT(te.id) as times_executed
FROM preventive_maintenance_plans p
JOIN preventive_maintenance_tasks t ON p.id = t.plan_id
LEFT JOIN preventive_maintenance_task_executions te ON t.id = te.task_id
GROUP BY p.id, p.plan_name, t.id, t.task_number, t.task_description, t.category, t.estimated_duration_minutes
ORDER BY p.plan_name, t.task_number;

-- ============================================
-- 8. TASK EXECUTION STATISTICS
-- ============================================
SELECT 
    t.task_number,
    t.task_description,
    COUNT(te.id) as total_executions,
    COUNT(CASE WHEN te.status = 'completed' THEN 1 END) as completed_count,
    COUNT(CASE WHEN te.status = 'skipped' THEN 1 END) as skipped_count,
    AVG(te.actual_duration_minutes) as avg_duration_minutes,
    MIN(te.actual_duration_minutes) as min_duration_minutes,
    MAX(te.actual_duration_minutes) as max_duration_minutes
FROM preventive_maintenance_tasks t
LEFT JOIN preventive_maintenance_task_executions te ON t.id = te.task_id
GROUP BY t.id, t.task_number, t.task_description
ORDER BY t.task_number;

-- ============================================
-- 9. EXECUTION DETAILS WITH TASK COMPLETION STATUS
-- ============================================
SELECT 
    pe.id as execution_id,
    pe.scheduled_date,
    m.name as machine_name,
    u.username as technician,
    pe.status,
    COUNT(te.id) as total_tasks,
    COUNT(CASE WHEN te.status = 'completed' THEN 1 END) as completed_tasks,
    ROUND(COUNT(CASE WHEN te.status = 'completed' THEN 1 END) * 100.0 / COUNT(te.id), 2) as completion_percentage,
    pe.total_duration_minutes
FROM preventive_maintenance_executions pe
LEFT JOIN machines m ON pe.machine_id = m.id
LEFT JOIN users u ON pe.assigned_technician_id = u.id
LEFT JOIN preventive_maintenance_task_executions te ON pe.id = te.execution_id
GROUP BY pe.id, pe.scheduled_date, m.name, u.username, pe.status, pe.total_duration_minutes
ORDER BY pe.scheduled_date DESC;

-- ============================================
-- 10. TECHNICIAN PERFORMANCE METRICS
-- ============================================
SELECT 
    u.username,
    u.first_name,
    u.last_name,
    COUNT(DISTINCT te.execution_id) as executions_performed,
    COUNT(te.id) as tasks_completed,
    ROUND(AVG(te.actual_duration_minutes), 2) as avg_task_duration_minutes,
    SUM(te.actual_duration_minutes) as total_maintenance_minutes,
    COUNT(CASE WHEN te.quality_check = 'passed' THEN 1 END) * 100.0 / COUNT(te.id) as quality_pass_percentage
FROM users u
LEFT JOIN preventive_maintenance_task_executions te ON u.id = te.technician_id
WHERE u.role = 'technician' AND te.status = 'completed'
GROUP BY u.id, u.username, u.first_name, u.last_name
ORDER BY executions_performed DESC;

-- ============================================
-- 11. CHECK FOR DATA INTEGRITY
-- ============================================
-- Check for orphaned task executions
SELECT COUNT(*) as orphaned_task_executions
FROM preventive_maintenance_task_executions te
WHERE NOT EXISTS (SELECT 1 FROM preventive_maintenance_executions pe WHERE pe.id = te.execution_id);

-- Check for missing task references
SELECT COUNT(*) as missing_task_references
FROM preventive_maintenance_task_executions te
WHERE NOT EXISTS (SELECT 1 FROM preventive_maintenance_tasks t WHERE t.id = te.task_id);

-- ============================================
-- 12. RECENT TASK EXECUTIONS (LAST 20)
-- ============================================
SELECT 
    pe.id as execution_id,
    te.id as task_exec_id,
    t.task_number,
    t.task_description,
    u.username as technician,
    te.status,
    te.start_time,
    te.end_time,
    te.actual_duration_minutes,
    te.quality_check,
    te.created_at
FROM preventive_maintenance_task_executions te
JOIN preventive_maintenance_executions pe ON te.execution_id = pe.id
LEFT JOIN preventive_maintenance_tasks t ON te.task_id = t.id
LEFT JOIN users u ON te.technician_id = u.id
ORDER BY te.created_at DESC
LIMIT 20;

-- ============================================
-- 13. AVERAGE TIME BY TASK (FOR PLANNING)
-- ============================================
SELECT 
    t.task_number,
    SUBSTRING(t.task_description, 1, 50) as task_name,
    t.estimated_duration_minutes,
    ROUND(AVG(te.actual_duration_minutes), 1) as avg_actual_duration,
    COUNT(te.id) as executions_count,
    ROUND(AVG(te.actual_duration_minutes) - t.estimated_duration_minutes, 1) as variance_minutes
FROM preventive_maintenance_tasks t
LEFT JOIN preventive_maintenance_task_executions te ON t.id = te.task_id AND te.status = 'completed'
GROUP BY t.id, t.task_number, t.task_description, t.estimated_duration_minutes
ORDER BY t.task_number;

-- ============================================
-- 14. QUALITY ISSUES TRACKING
-- ============================================
SELECT 
    t.task_number,
    SUBSTRING(t.task_description, 1, 40) as task,
    COUNT(CASE WHEN te.quality_check = 'failed' THEN 1 END) as failed_checks,
    COUNT(te.id) as total_executions,
    ROUND(COUNT(CASE WHEN te.quality_check = 'failed' THEN 1 END) * 100.0 / COUNT(te.id), 2) as failure_rate_percent
FROM preventive_maintenance_tasks t
LEFT JOIN preventive_maintenance_task_executions te ON t.id = te.task_id AND te.status = 'completed'
GROUP BY t.id, t.task_number, t.task_description
HAVING COUNT(CASE WHEN te.quality_check = 'failed' THEN 1 END) > 0
ORDER BY failed_checks DESC;

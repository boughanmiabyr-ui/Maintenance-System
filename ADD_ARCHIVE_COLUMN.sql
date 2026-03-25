-- Migration: Add archive_date column and update demand_status enum for archive system
-- Date: 2026-03-12
-- Description: Adds archive_date column to track when demands are archived
--             Updates demand_status enum to include 'archived' and 'cancelled' statuses

USE maintenance_system_v2;

-- Step 1: Update the demand_status ENUM to include 'archived' and 'cancelled'
ALTER TABLE spare_parts_demands 
MODIFY COLUMN demand_status ENUM(
    'pending',
    'supervisor_review',
    'approved_supervisor',
    'stock_agent_review',
    'approved_stock_agent',
    'rejected',
    'partial_allocated',
    'fulfilled',
    'cancelled',
    'archived'
) DEFAULT 'pending';

-- Step 2: Add archive_date column to track when a demand was archived
ALTER TABLE spare_parts_demands 
ADD COLUMN archive_date DATETIME NULL AFTER updated_at;

-- Step 3: Create index on archive_date for faster filtering of archived demands
ALTER TABLE spare_parts_demands 
ADD INDEX idx_archive_date (archive_date);

-- Step 4: Create index on demand_status and archive_date for quick filtering
ALTER TABLE spare_parts_demands 
ADD INDEX idx_status_archived (demand_status, archive_date);

-- Verification: Show the updated table structure
DESCRIBE spare_parts_demands;

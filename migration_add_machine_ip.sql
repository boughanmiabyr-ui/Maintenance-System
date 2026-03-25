-- SQL Migration: Add IP Address and Zone to Machines Table
-- This script adds the new columns to support Raspberry Pi integration
-- Compatible with MySQL 5.7+

-- Add ip_address column
ALTER TABLE machines ADD COLUMN ip_address VARCHAR(50) NULL UNIQUE;
CREATE INDEX idx_machines_ip_address ON machines(ip_address);

-- Add machine_name column
ALTER TABLE machines ADD COLUMN machine_name VARCHAR(200) NULL;

-- Add zone column
ALTER TABLE machines ADD COLUMN zone VARCHAR(100) NULL;
CREATE INDEX idx_machines_zone ON machines(zone);

-- Add zone_id column (for relationship with zones table)
ALTER TABLE machines ADD COLUMN zone_id INT NULL;
ALTER TABLE machines ADD CONSTRAINT fk_machines_zones FOREIGN KEY (zone_id) REFERENCES zones(id) ON DELETE SET NULL;

-- ============================================
-- EXAMPLE: Update existing machines
-- ============================================

-- Update machine M001 with IP address
UPDATE machines SET ip_address = '10.110.30.15' WHERE machine_code = 'M001';

-- Update machine M002 with IP address
UPDATE machines SET ip_address = '10.110.30.16' WHERE machine_code = 'M002';

-- Update machine M003 with IP address
UPDATE machines SET ip_address = '10.110.30.17' WHERE machine_code = 'M003';

-- Set machine names
UPDATE machines SET machine_name = 'Assembly Line 1' WHERE machine_code = 'M001';
UPDATE machines SET machine_name = 'Assembly Line 2' WHERE machine_code = 'M002';

-- Set zones
UPDATE machines SET zone = 'Production Zone A' WHERE machine_code = 'M001';
UPDATE machines SET zone = 'Production Zone B' WHERE machine_code = 'M002';

-- ============================================
-- VERIFY: Check if columns were added
-- ============================================

-- View all machines with new columns
SELECT machine_code, machine_name, ip_address, zone, department FROM machines;

-- Check machines without IP addresses
SELECT machine_code, machine_name FROM machines WHERE ip_address IS NULL;

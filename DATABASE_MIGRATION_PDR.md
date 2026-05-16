# Database Migration Guide - PDR (Spare Parts) Fields

## Overview
This guide provides instructions for adding the new Spare Parts (PDR) fields to existing database schemas.

---

## Pre-Migration Checklist

- [ ] Backup your database
- [ ] Test migration on a development/staging environment first
- [ ] Schedule migration during maintenance window (if applicable)
- [ ] Notify users about the update
- [ ] Prepare rollback plan

---

## Migration Scripts

### Option 1: Using Alembic (Recommended for Flask Applications)

If using Flask-Migrate with Alembic, create a new migration:

```bash
flask db migrate -m "Add PDR fields to materials and inventory"
flask db upgrade
```

### Option 2: Direct SQL Migration

#### Step 1: Backup Your Database
```sql
-- PostgreSQL
COPY materials TO PROGRAM 'gzip > /backup/materials_backup.sql.gz';
COPY inventory TO PROGRAM 'gzip > /backup/inventory_backup.sql.gz';

-- MySQL
mysqldump -u username -p database_name > backup_before_migration.sql

-- SQLite
.backup '/backup/database_backup.db'
```

#### Step 2: Add New Columns to Materials Table

**PostgreSQL/SQLite:**
```sql
ALTER TABLE materials ADD COLUMN lifespan_days INTEGER;
ALTER TABLE materials ADD COLUMN stock_entry_date TIMESTAMP;
ALTER TABLE materials ADD COLUMN stock_registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- For existing records, set registration date to creation date
UPDATE materials 
SET stock_registration_date = created_at 
WHERE stock_registration_date IS NULL;
```

**MySQL:**
```sql
ALTER TABLE materials ADD COLUMN lifespan_days INT;
ALTER TABLE materials ADD COLUMN stock_entry_date DATETIME;
ALTER TABLE materials ADD COLUMN stock_registration_date DATETIME DEFAULT CURRENT_TIMESTAMP;

-- For existing records, set registration date to creation date
UPDATE materials 
SET stock_registration_date = created_at 
WHERE stock_registration_date IS NULL;
```

#### Step 3: Add New Columns to Inventory Table

**PostgreSQL/SQLite:**
```sql
ALTER TABLE inventory ADD COLUMN stock_entry_date TIMESTAMP;
```

**MySQL:**
```sql
ALTER TABLE inventory ADD COLUMN stock_entry_date DATETIME;
```

#### Step 4: Add Indexes for Performance (Optional)

```sql
CREATE INDEX idx_materials_stock_entry ON materials(stock_entry_date);
CREATE INDEX idx_materials_registration ON materials(stock_registration_date);
CREATE INDEX idx_inventory_stock_entry ON inventory(stock_entry_date);
```

#### Step 5: Verify Migration

```sql
-- Check if new columns exist in materials table
SELECT * FROM materials LIMIT 1;

-- Check if new columns exist in inventory table
SELECT * FROM inventory LIMIT 1;

-- Verify data integrity
SELECT COUNT(*) FROM materials WHERE stock_registration_date IS NOT NULL;
```

---

## Option 3: Python Script Migration

Use this Python script if you prefer to migrate programmatically:

```python
from app import db, create_app
from app.models import Material, Inventory
from datetime import datetime

def migrate_pdr_fields():
    """Migrate PDR fields for existing records"""
    app = create_app()
    
    with app.app_context():
        try:
            # Migrate Materials
            print("Migrating Materials table...")
            materials = Material.query.all()
            
            for material in materials:
                # Set registration date to creation date if null
                if material.stock_registration_date is None:
                    material.stock_registration_date = material.created_at
                
                # Optional: Set stock_entry_date to created_at if null
                # material.stock_entry_date = material.created_at
                
            db.session.commit()
            print(f"✓ Migrated {len(materials)} materials")
            
            # Migrate Inventory
            print("Migrating Inventory table...")
            inventory_items = Inventory.query.all()
            
            for item in inventory_items:
                # Optional: Set stock_entry_date for inventory batches
                if item.stock_entry_date is None:
                    item.stock_entry_date = item.created_at
            
            db.session.commit()
            print(f"✓ Migrated {len(inventory_items)} inventory items")
            
            print("\n✅ Migration completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Migration failed: {str(e)}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    migrate_pdr_fields()
```

Run the migration script:
```bash
python migrate_pdr.py
```

---

## Post-Migration Verification

### 1. Verify Column Creation
```python
from app import create_app
from app.models import Material, Inventory
from sqlalchemy import inspect

app = create_app()
with app.app_context():
    # Check Material columns
    material_columns = [c.name for c in inspect(Material).columns]
    print("Material columns:", material_columns)
    
    # Check Inventory columns
    inventory_columns = [c.name for c in inspect(Inventory).columns]
    print("Inventory columns:", inventory_columns)
    
    # Verify data
    materials = Material.query.limit(5).all()
    for mat in materials:
        print(f"Material: {mat.designation}")
        print(f"  - Lifespan: {mat.lifespan_days}")
        print(f"  - Entry Date: {mat.stock_entry_date}")
        print(f"  - Registration Date: {mat.stock_registration_date}")
```

### 2. Test Application
- [ ] Log in to the application
- [ ] View material list - check new columns display
- [ ] Add a new material - verify new fields are saved
- [ ] Edit existing material - verify new fields can be updated
- [ ] Check material details - verify PDR information displays

### 3. Verify Data Integrity
```sql
-- Count records with registration dates
SELECT COUNT(*) as total_with_dates 
FROM materials 
WHERE stock_registration_date IS NOT NULL;

-- Check for any NULL registration dates (should be 0 after migration)
SELECT COUNT(*) as nulls 
FROM materials 
WHERE stock_registration_date IS NULL;
```

---

## Rollback Procedure

If migration needs to be rolled back:

### Using Alembic:
```bash
flask db downgrade  # Downgrade one revision
# or
flask db downgrade -1  # Go back one specific revision
```

### Manual Rollback:
```sql
-- Drop new columns
ALTER TABLE materials DROP COLUMN lifespan_days;
ALTER TABLE materials DROP COLUMN stock_entry_date;
ALTER TABLE materials DROP COLUMN stock_registration_date;

ALTER TABLE inventory DROP COLUMN stock_entry_date;

-- Drop indexes if created
DROP INDEX idx_materials_stock_entry;
DROP INDEX idx_materials_registration;
DROP INDEX idx_inventory_stock_entry;
```

### Restore from Backup:
```bash
# PostgreSQL
gunzip -c /backup/materials_backup.sql.gz | psql database_name

# MySQL
mysql -u username -p database_name < backup_before_migration.sql

# SQLite
.restore '/backup/database_backup.db'
```

---

## Troubleshooting

### Issue: Column already exists
**Solution:** Verify if migration was already applied. Check `alembic_version` table.

```sql
SELECT version_num FROM alembic_version;
```

### Issue: Data type mismatch
**Solution:** Ensure database-specific datetime syntax:
- PostgreSQL: `TIMESTAMP`
- MySQL: `DATETIME`
- SQLite: `DATETIME` or `TIMESTAMP`

### Issue: Migration script not running
**Solution:** 
1. Verify database connection
2. Check user permissions (ALTER TABLE privilege)
3. Ensure no active connections to database tables

```sql
-- Check active connections (PostgreSQL)
SELECT * FROM pg_stat_activity WHERE datname = 'your_database';

-- Kill sessions if needed
SELECT pg_terminate_backend(pid) FROM pg_stat_activity 
WHERE datname = 'your_database' AND pid <> pg_backend_pid();
```

---

## Performance Considerations

### Index Strategy
The following indexes are recommended for optimal performance:

```sql
-- For filtering/sorting by dates
CREATE INDEX idx_stock_entry_date ON materials(stock_entry_date);
CREATE INDEX idx_stock_registration_date ON materials(stock_registration_date);

-- For inventory batch tracking
CREATE INDEX idx_inventory_stock_entry ON inventory(stock_entry_date);

-- Composite indexes for common queries
CREATE INDEX idx_materials_status_entry 
ON materials(status, stock_entry_date);
```

### Query Optimization
Ensure the following queries have good performance:

```sql
-- Find parts approaching end-of-life
SELECT * FROM materials 
WHERE stock_entry_date + (lifespan_days || ' days')::INTERVAL <= NOW()
AND status = 'active';

-- Find critical stock with entry date
SELECT m.designation, m.current_stock, m.stock_entry_date, m.lifespan_days
FROM materials m
WHERE m.current_stock <= m.min_stock
ORDER BY m.stock_entry_date ASC;
```

---

## Validation Checklist

After migration completion, verify:

- [ ] All new columns created successfully
- [ ] No data loss occurred
- [ ] Registration dates populated for existing records
- [ ] Application starts without errors
- [ ] Material add form works with new fields
- [ ] Material edit form displays all fields
- [ ] Material list shows new columns
- [ ] Spare parts inventory shows all new information
- [ ] No performance degradation observed
- [ ] Error logs are clean
- [ ] User interface displays dates correctly

---

## Version Information

| Component | Version |
|-----------|---------|
| Python | 3.8+ |
| Flask | 2.0+ |
| SQLAlchemy | 1.3+ |
| Flask-SQLAlchemy | 2.4+ |

---

## Support

For issues or questions during migration:
1. Check the troubleshooting section
2. Review application logs
3. Verify database connectivity
4. Contact system administrator


# PDR (Spare Parts) Information Guide

## Overview
This document outlines the new Spare Parts (PDR - Pièce De Rechange) information fields that have been added to the maintenance system for comprehensive inventory tracking.

---

## New Fields Added to Spare Parts Management

### 1. **Current Stock**
- **Description**: The actual quantity of the spare part currently available in inventory
- **Location**: Inventory table, linked to Material and StockLocation
- **Purpose**: Tracks real-time stock levels at different warehouse locations
- **Data Type**: Integer
- **Usage**: Displayed in all inventory views, compared against Min/Max levels

### 2. **Minimum/Maximum Stock Levels**
- **Minimum Stock** (`min_quantity`)
  - **Description**: Threshold level that triggers reordering alerts
  - **Purpose**: System alerts when stock falls below this level
  - **Usage**: Auto-generates low-stock alerts
  
- **Maximum Stock** (`max_quantity`)
  - **Description**: Recommended maximum storage level
  - **Purpose**: Prevents over-ordering and optimizes storage
  - **Usage**: Used in capacity planning and stock status determination

### 3. **Unit Cost**
- **Field Name**: `unit_price_eur`
- **Description**: Cost per unit of the spare part in EUR
- **Purpose**: 
  - Calculates total inventory value
  - Assists in procurement planning
  - Budget tracking for maintenance operations
- **Data Type**: Float
- **Usage**: Displayed in material details and inventory views

### 4. **Lifespan**
- **Field Name**: `lifespan_days`
- **Description**: Expected useful life of the spare part in days
- **Purpose**: 
  - Determines when parts may become obsolete
  - Helps plan replacement schedules
  - Identifies parts approaching end-of-life
- **Data Type**: Integer (days)
- **Optional**: Yes (can be null if not applicable)
- **Usage**: Displayed in spare parts inventory, useful for maintenance scheduling

### 5. **Stock Entry Date**
- **Field Name**: `stock_entry_date` (on Material model)
- **Description**: Date when the spare part batch/unit is first received into inventory
- **Purpose**: 
  - Tracks stock age
  - Helps identify FIFO (First In, First Out) requirements
  - Determines part expiration based on lifespan
- **Data Type**: DateTime
- **Optional**: Yes
- **Added To**: 
  - Material table (for material-level tracking)
  - Inventory table (for batch-level tracking)
- **Usage**: Helps manage stock rotation and quality control

### 6. **Stock Registration Date**
- **Field Name**: `stock_registration_date`
- **Description**: The date and time when the spare part is registered/created in the system
- **Purpose**: 
  - Audit trail for system records
  - Tracks when inventory item was first entered
  - System documentation
- **Data Type**: DateTime
- **Auto-Generated**: Yes - automatically set to current timestamp on creation
- **Immutable**: Yes - cannot be changed after registration
- **Usage**: Read-only field, used for compliance and audit purposes

---

## Database Schema Updates

### Material Table Updates
```python
class Material(db.Model):
    __tablename__ = 'materials'
    
    # Existing fields
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(50), unique=True, nullable=False)
    designation = db.Column(db.String(255), nullable=False)
    min_quantity = db.Column(db.Integer, default=1)
    max_quantity = db.Column(db.Integer, default=100)
    unit_price_eur = db.Column(db.Float, nullable=False)
    
    # NEW FIELDS
    lifespan_days = db.Column(db.Integer, nullable=True)
    stock_entry_date = db.Column(db.DateTime)
    stock_registration_date = db.Column(db.DateTime, default=datetime.utcnow)
```

### Inventory Table Updates
```python
class Inventory(db.Model):
    __tablename__ = 'inventory'
    
    # Existing fields
    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('stock_locations.id'), nullable=False)
    quantity_on_hand = db.Column(db.Integer, default=0)
    quantity_reserved = db.Column(db.Integer, default=0)
    
    # NEW FIELD
    stock_entry_date = db.Column(db.DateTime)  # For batch tracking
```

---

## Updated Forms and Templates

### Add Material Form
The following new fields are included:
- **Stock Entry Date** (Optional, date picker)
- **Lifespan (Days)** (Optional, numeric input)
- **Stock Registration Date** (Auto-generated, displayed only on edit)

### Edit Material Form
All new fields can be edited except:
- **Stock Registration Date** (read-only, auto-generated)

### Spare Parts Inventory View
The browse spare parts table now displays:
- Current Stock with Min/Max levels
- Unit Cost (EUR)
- Lifespan (days)
- Stock Entry Date
- Stock Registration Date
- Status (Critical/Warning/Normal)

---

## User Interface Changes

### Stock Management Page
- **New columns in inventory table**:
  1. Code
  2. Part Name
  3. Current Stock
  4. Min/Max Stock Levels
  5. Unit Cost
  6. Lifespan
  7. Stock Entry Date
  8. Registration Date
  9. Status
  10. Actions

### Material Detail View
- New section: "Spare Part Registration (PDR)"
  - Shows Stock Entry Date
  - Shows Stock Registration Date (auto-generated)
  - Shows Lifespan information

---

## Business Logic & Rules

### Stock Status Calculation
```
IF current_stock <= min_quantity:
    Status = "CRITICAL" (Red badge)
ELSE IF current_stock <= (max_quantity * 0.5):
    Status = "WARNING" (Yellow badge)
ELSE:
    Status = "NORMAL" (Green badge)
```

### Age Calculation (Optional Feature)
Parts can be marked as approaching expiration if:
```
stock_entry_date + lifespan_days <= today
    → Display expiration warning
```

### Inventory Value Calculation
```
Total Inventory Value = current_stock * unit_price_eur
```

---

## Implementation Notes

### Migration Steps (if upgrading existing database)
1. Add new columns to materials table
2. Add new columns to inventory table
3. Set default `stock_registration_date = NOW()` for existing records
4. Populate `stock_entry_date` with `created_at` date for migration

### Default Behaviors
- `lifespan_days`: Null (optional field)
- `stock_entry_date`: Null (optional field)
- `stock_registration_date`: Auto-generated (current timestamp)

### API Considerations
When creating new materials via API:
- `stock_registration_date` is auto-generated
- `stock_entry_date` can be provided or will be null
- `lifespan_days` is optional

---

## Benefits

1. **Better Inventory Management**
   - Track current stock, min/max levels, and unit costs
   - Identify critical/warning stock situations

2. **Cost Tracking**
   - Calculate total inventory value
   - Monitor spare part expenses

3. **Quality Control**
   - Track part age and lifespan
   - Manage obsolescence
   - Support FIFO rotation

4. **Compliance & Audit**
   - Auto-generated registration dates
   - Complete audit trail of part entry

5. **Maintenance Planning**
   - Use lifespan data for preventive maintenance
   - Plan part replacement cycles

---

## Support & Maintenance

For questions or issues related to PDR functionality:
1. Check the material detail page for complete spare part information
2. Review stock status indicators (Critical/Warning/Normal)
3. Contact the system administrator for configuration changes

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-05-10 | Initial implementation of PDR fields |
| | | Added lifespan_days, stock_entry_date, stock_registration_date |
| | | Updated Material and Inventory models |
| | | Updated all related templates and forms |


# Spare Parts Demand Archive System Implementation

## Overview
A comprehensive archive system has been implemented for spare parts demands. This allows finished demands (fulfilled, rejected, or cancelled) to be moved to an archive, removed from the active list, and retrieved with filtering capabilities.

## Changes Made

### 1. **Database Schema Updates**

#### Model Updates (app/models/updated_models.py)
- Added `ARCHIVED = 'archived'` status to the `DemandStatus` Enum
- Added `archive_date` column to `SparePartsDemand` model:
  - Type: `DateTime`, nullable
  - Records when a demand was archived
  - Allows filtering by archive date

#### Enum Updates (app/models/__init__.py)
- Added `ARCHIVED = 'archived'` and `CANCELLED = 'cancelled'` to `DemandStatus` Enum

### 2. **Backend Routes (app/routes/demands.py)**

#### Updated Routes:

**1. `list_demands()` - Modified to exclude archived demands**
   - Added `show_archived` parameter to optionally display archived demands
   - Filters out archived demands by default when viewing active demands
   - Shows archived_count badge on the header
   - Status counts exclude archived demands in active view

**2. `archive_demand(demand_id)` - NEW ROUTE**
   - **URL**: `POST /demands/<int:demand_id>/archive`
   - **Roles**: stock_agent, supervisor, admin
   - **Purpose**: Archive a finished demand and all items in its group
   - **Allowed Status**: fulfilled, approved_stock_agent, rejected, cancelled
   - **Actions**:
     - Sets demand status to 'archived'
     - Records archive_date as current timestamp
     - Archives entire demand group
   - **Permissions**: Must be associated with the demand (requestor, supervisor, or stock agent)

**3. `archived_demands()` - NEW ROUTE**
   - **URL**: `GET /demands/archived`
   - **Purpose**: View all archived demands with filtering
   - **Features**:
     - Paginates archived demands (20 per page)
     - Groups demands by base demand number
     - Role-based filtering (same logic as active demands)
     - Date filtering options:
       - All time
       - Archived today
       - Archived this week
       - Archived this month
     - Shows archive date/time for each demand
   - **Permissions**: User can see only archived demands they're associated with

**4. `restore_archived_demand(demand_id)` - NEW ROUTE**
   - **URL**: `POST /demands/archived/<int:demand_id>/restore`
   - **Roles**: stock_agent, supervisor, admin
   - **Purpose**: Restore an archived demand back to active list
   - **Actions**:
     - Changes demand status from 'archived' back to 'fulfilled'
     - Clears the archive_date
     - Restores entire demand group
   - **Use Case**: If an archived demand needs to be reopened or corrected

### 3. **Templates**

#### Updated Templates:

**1. [demands/list.html](../app/templates/demands/list.html) - Modified**
   - Added "Archived" button in header showing count of archived demands
   - Links to archived demands list
   - Added "Archive" button to Actions column for finished demands
   - Archive button only appears for status: fulfilled, approved_stock_agent, rejected, cancelled

**2. [demands/detail.html](../app/templates/demands/detail.html) - Modified**
   - Added "Archive" button in top-right corner
   - Only visible for finished demands
   - Allows archiving directly from demand detail view

**3. [demands/archived.html](../app/templates/demands/archived.html) - NEW TEMPLATE**
   - Displays list of archived demands
   - Shows archive date/time with day name
   - Date filter options (today, week, month, all time)
   - "View" and "Restore" action buttons
   - Pagination support (20 per page)
   - Empty state message

## Workflow

### Archiving a Demand:
1. Staff member completes a demand (status: fulfilled, approved_stock_agent, rejected, or cancelled)
2. Click "Archive" button on:
   - Demand list page (in Actions column)
   - Demand detail page (top-right corner)
3. Demand is moved to archive with current timestamp
4. Demand disappears from active list
5. Email notifications can be added if needed

### Viewing Archived Demands:
1. Click "Archived (N)" button in demands list header
2. Filter by archive date if needed:
   - Today
   - This Week
   - This Month
   - All Time
3. View demand details
4. Optionally restore to active list

### Restoring a Demand:
1. Open archived demands list
2. Find the demand
3. Click "Restore" button
4. Confirm action
5. Demand returns to "fulfilled" status in active list

## Permissions

- **Technicians**: Can see archived demands they requested
- **Supervisors**: Can see archived demands they supervised or requested
- **Stock Agents**: Can see archived demands they allocated or were requested by them
- **Admins**: Can see and manage all archived demands

## Database Considerations

### New Column:
- `spare_parts_demands.archive_date` - DateTime nullable field
- No data loss; archived demands remain in database with archive status

### Performance:
- Archived demands are naturally filtered out of active queries
- Separate archive view reduces clutter in active demand management
- Can implement periodic archival policies if needed

### Migration:
- No migration code is auto-generated; this depends on your Flask-SQLAlchemy setup
- When deployed, run `flask db migrate` and `flask db upgrade` if using Flask-Migrate

## Usage Examples

### Query Active Demands (excludes archived):
```python
active_demands = SparePartsDemand.query.filter(
    SparePartsDemand.demand_status != 'archived'
).all()
```

### Query Archived Demands:
```python
archived_demands = SparePartsDemand.query.filter_by(
    demand_status='archived'
).all()
```

### Filter Archived This Week:
```python
from datetime import datetime, timedelta

week_ago = datetime.utcnow() - timedelta(days=7)
recently_archived = SparePartsDemand.query.filter(
    (SparePartsDemand.demand_status == 'archived') &
    (SparePartsDemand.archive_date >= week_ago)
).all()
```

## Future Enhancements

Possible additions:
1. **Scheduled Archival**: Automatically archive fulfilled demands after N days
2. **Bulk Operations**: Archive multiple demands at once
3. **Archive Reports**: Generate reports on archived demands by date/user/material
4. **Soft Delete**: Optional permanent deletion with additional confirmation
5. **Archive Search**: Full-text search within archived demands
6. **Export**: Export archived demands to CSV/Excel
7. **Archive Notifications**: Email confirmation when demands are archived
8. **Audit Trail**: Track archive/restore actions with timestamps and user info

## Testing Checklist

- [ ] Create a spare parts demand and complete it (mark as fulfilled)
- [ ] Verify "Archive" button appears on completed demands
- [ ] Click Archive and confirm demand moves to archived list
- [ ] Verify archived demand no longer appears in active list
- [ ] Access archived demands list via "Archived (N)" button
- [ ] Test date filters on archived list
- [ ] Verify pagination works (if >20 archived)
- [ ] Click "Restore" on archived demand
- [ ] Confirm demand returns to active fulfiled status
- [ ] Test permissions for different user roles
- [ ] Verify role-based filtering in archived view

## Notes

- Archive dates are stored in UTC (datetime.utcnow())
- Archived demands keep all historical data (approvals, allocations, etc.)
- Archive operation is reversible via restore function
- No emails are sent on archive by default (can be added)
- Status cascade: FULFILLED → ARCHIVED → FULFILLED (if restored)

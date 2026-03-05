# Power BI Dashboard Template for Maintenance & Stock KPIs

This document outlines a professional Power BI report structure that you can use to visualize the two KPI sets calculated by your Flask application:

- **Maintenance KPIs**
- **Stock KPIs**

The template includes the necessary database connection steps, queries, calculated measures and visual layout guidance. You can save this as part of your project or use it to build a `.pbit` report template.

---

## 1. Database Connection

1. Open Power BI Desktop.
2. Select **Get Data > SQL Server** (or your DB provider).
3. Enter the server name and database name where your Flask app stores data (check `config.py` for `SQLALCHEMY_DATABASE_URI`).
4. Choose **Import** for better performance, or **DirectQuery** if you want live data.
5. Click **OK** and authenticate with the appropriate credentials.


## 2. Import Tables

Load at least the following tables/views:

- `maintenance_report` (or whichever model table name corresponds to `MaintenanceReport`)
- `stock_movement`
- `material`
- `user` (for technician names)

Optionally include `maintenance_schedule` or other lookup tables if needed for filtering.


## 3. Data Model & Relationships

Ensure relationships exist:

- `maintenance_report.technician_id` → `user.id`
- `stock_movement.material_id` → `material.id`

Mark date columns (`created_at`, `scheduled_date`) as `Date` types and add them to a calendar table if you need time intelligence.


## 4. Measures (DAX)

### Maintenance KPIs

```dax
TotalEvents = COUNT('maintenance_report'[id])

TotalDowntimeHours =
SUM('maintenance_report'[actual_duration_hours])

CanceledEvents =
CALCULATE(
    COUNT('maintenance_report'[id]),
    'maintenance_report'[report_status] = "rejected"
)

OperationalHours =
DATEDIFF(
    MIN('calendar'[Date]),
    MAX('calendar'[Date]),
    HOUR
)

AvailabilityRate =
VAR downtime = [TotalDowntimeHours]
VAR opHours = [OperationalHours]
RETURN
IF(opHours > 0, (1 - downtime / opHours) * 100, 0)

FailureRate =
DIVIDE( [CanceledEvents], [TotalDowntimeHours], 0 )

MTTR =
AVERAGE('maintenance_report'[actual_duration_hours]) * 3600

MTBF =
DIVIDE( [OperationalHours], [CanceledEvents], 0 )
```

Add calculated columns for `ReportType` counts if desired.

### Stock KPIs

```dax
TotalSpareParts = COUNT('material'[id])

TotalStockValue =
SUMX('material', 'material'[current_stock] * 'material'[unit_cost])

LowStockItems =
CALCULATE(COUNT('material'[id]), 'material'[current_stock] <= 'material'[min_stock])

OverstockItems =
CALCULATE(COUNT('material'[id]), 'material'[current_stock] >= 'material'[max_stock])

CriticalItems =
CALCULATE(
    COUNT('material'[id]),
    OR('material'[current_stock] = 0, 'material'[current_stock] <= 'material'[reorder_point])
)

AvgStockLevel = AVERAGE('material'[current_stock])

StockIn =
CALCULATE(
    SUM('stock_movement'[quantity]),
    'stock_movement'[movement_type] IN {"in","receipt"}
)

StockOut =
CALCULATE(
    SUM('stock_movement'[quantity]),
    'stock_movement'[movement_type] IN {"out","issue","allocated"}
)
```


## 5. Report Layout

1. **Title Page** – add a report title (e.g., "Maintenance & Stock KPI Dashboard") and a logo if available.
2. **Date slicer** – include a slicer using your calendar table to limit the period.
3. **KPI Cards** – display the key measures (Total Events, Downtime, Availability, etc.) as cards.
4. **Charts**:
   - Bar chart of events per machine (`machine_name` vs count).
   - Donut/pie for report status distribution.
   - Column chart for stock categories or movement summary.
5. **Tables** – include tables for most active technicians, top value materials, etc.
6. **Filters** – allow filtering by technician, machine, or category using slicers.


## 6. Save as Template

Once the report is built:

- Choose **File > Export > Power BI template**.
- Provide a meaningful name like `Maintenance_Stock_KPI_Template.pbit`.
- The template will save the report structure and queries but not the data.

Users can then open the `.pbit`, enter their database connection details, and immediately see the dashboard with their own data.

---

💡 **Tip:** You can embed your existing SQL logic directly in Power Query by using `Value.NativeQuery` with the same filters shown in `main.py` for start/end dates.

This document should give you a professional starting point for crafting a Power BI dashboard that mirrors the KPIs computed by your Flask backend.
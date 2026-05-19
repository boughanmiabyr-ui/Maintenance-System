# Add Quantity Feature - Documentation

## Overview

The **Add Quantity** feature allows stock agents to quickly update the quantity of existing spare parts (PDR) in the inventory without creating duplicate items. When receiving new orders or inventory corrections, users can search for an existing material and increase its stock in just a few clicks.

## Feature Location

- **Page**: Stock Management → Add New Material (`/stock/add`)
- **Button**: Blue "Add Quantity" button in the top right section
- **Accessible to**: Admin, Stock Agent roles

## How It Works

### 1. Accessing the Feature

1. Navigate to **Stock Management** → **Add New Material**
2. Click the blue **"Add Quantity"** button (with plus icon)
3. A modal dialog will open with search functionality

### 2. Search for Existing Material

The search bar accepts queries in three fields:
- **Material Code**: Unique identifier (e.g., "MAT-001", "293")
- **Material Name**: Full or partial name
- **Category**: Material category

**Example searches:**
- "293" - Searches for material code 293
- "Ruban" - Searches for any material with "Ruban" in name
- "Adhésifs" - Searches for materials in Adhésifs category

### 3. Select Material

- Search results display with:
  - Material code and name
  - Current stock quantity
  - Stock status badge (Normal/Warning/Critical)
  - Category information
  - Unit of measure

- Click the **"Select"** button on any result to choose that material

### 4. Update Quantity

Once a material is selected:
1. Material details appear in the **Update Quantity** section showing:
   - Current stock level
   - Stock status
   - Unit of measure
   
2. Enter the quantity to add (must be positive number)
3. (Optional) Add a reason for the update (e.g., "Received order", "Inventory correction")
4. Click **"Update Stock"** button

### 5. Confirmation

- System shows success message with new total quantity
- Stock movement record is automatically created
- Modal closes and form resets for next operation

## Backend Implementation

### API Endpoints

#### 1. Search Materials
```
POST /api/materials/search
Headers: Content-Type: application/json

Request Body:
{
  "query": "search_term"
}

Response:
{
  "success": true,
  "results": [
    {
      "id": 115,
      "code": "293",
      "name": "Ruban Jaune 50mmx33m",
      "category": "Adhésifs",
      "unit": "Rouleau",
      "current_stock": 85,
      "min_stock": 10,
      "max_stock": 500,
      "stock_status": "normal",
      "unit_cost": 15.50,
      "supplier": "Supplier Name"
    }
  ]
}
```

#### 2. Update Material Quantity
```
POST /api/materials/update-quantity
Headers: Content-Type: application/json

Request Body:
{
  "material_id": 115,
  "quantity": 50,
  "reason": "Received order from supplier"
}

Response:
{
  "success": true,
  "message": "Stock updated successfully. New quantity: 135",
  "new_stock": 135
}
```

### Database Changes

**Stock Movement Record Created:**
- Type: 'in' (inbound)
- Quantity: Amount added
- Notes: Reason provided by user
- User: Automatically recorded
- Timestamp: Recorded automatically

**Material Record Updated:**
- `current_stock`: Increased by quantity
- `last_restocked`: Updated to current time

## Key Features

### Smart Search
- Case-insensitive search
- Partial matching on code, name, and category
- Returns up to 20 matching results
- Real-time feedback with loading indicator

### Stock Status Display
- **Green (Normal)**: Stock within acceptable range
- **Yellow (Warning)**: Stock approaching reorder point or exceeds max
- **Red (Critical)**: Stock below minimum level

### Validation
- Quantity must be positive number
- Material must exist in database
- Only authorized roles can access
- All operations are logged with user ID and timestamp

### Audit Trail
Each stock update creates a StockMovement record with:
- Material ID
- Quantity added
- Type: 'in'
- User ID who performed update
- Reason/notes
- Timestamp

## User Interface Elements

### Modal Components

**Search Section:**
- Input field for search term
- Search button (with icon)
- Loading indicator during search
- Results list (scrollable, max 20 items)
- "No results" message

**Result Items:**
- Code and name
- Current stock with unit
- Stock status badge
- Select button

**Update Section (appears after selection):**
- Material info card (read-only)
- Quantity input field
- Reason input field (optional)
- Update Stock button

## Error Handling

The feature includes comprehensive error handling:
- Invalid search queries → "No materials found" message
- Network errors → "Error searching materials" message
- Missing quantity → Alert: "Please enter a valid quantity"
- Failed update → Error message from server
- Material not found → "Material not found" error

## Role-Based Access

- **Admin**: Full access to all features
- **Stock Agent**: Full access to all features
- **Other Roles**: No access (feature button not visible)

## Best Practices

### When to Use "Add Quantity"
✓ Receiving new orders of existing parts
✓ Inventory corrections after stock audit
✓ Restocking existing materials
✓ Adding returned items back to inventory

### When NOT to Use
✗ Adding completely new materials (use "Add New Material" form)
✗ Removing stock (use returns or allocation features)
✗ Updating pricing or supplier info (use edit material)

## Performance Considerations

- Search limited to 20 results for performance
- Case-insensitive search using SQL LIKE
- Stock movement records indexed by material_id
- Immediate database commit for consistency

## Related Features

- **Add New Material**: Create new spare parts from scratch
- **Edit Material**: Modify material details, pricing, limits
- **Material Detail**: View full history and recent transactions
- **Stock Alerts**: Automatic alerts for low/high stock
- **Movement History**: View all stock in/out transactions

## Testing

The feature includes automated tests verifying:
- Material model structure
- StockMovement model creation
- Search functionality
- API endpoint registration
- Database operations

Run tests:
```bash
python test_add_quantity_feature.py
```

## Troubleshooting

**Feature button not appearing:**
- Check user role (must be Admin or Stock Agent)
- Reload page to refresh permissions

**Search returns no results:**
- Try shorter search term
- Check exact spelling (search is case-insensitive but partial match)
- Material might be inactive

**Update fails with error:**
- Check network connection
- Verify quantity is a positive number
- Material may have been deleted
- Check browser console (F12) for error details

**Stock not updating:**
- Refresh page to see updated quantity
- Check Material Detail page for stock history
- Verify sufficient database disk space

## Future Enhancements

Potential improvements for future versions:
- Bulk quantity updates for multiple materials
- CSV import for stock updates
- Quantity presets (common restock amounts)
- Email notifications on stock updates
- Barcode/QR code scanning for material selection
- Historical stock level charts
- Automated reorder suggestions

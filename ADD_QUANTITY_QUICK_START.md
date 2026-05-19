# Add Quantity Feature - Quick Start Guide

## 🚀 Quick Start (30 seconds)

### Step 1: Navigate to Add Material Page
```
Stock Management → Add New Material
```

### Step 2: Click "Add Quantity" Button
Look for the blue button in the top right with a **+** icon

### Step 3: Search for Spare Part
Type in the search box:
- **Material code** (e.g., "293")
- **Material name** (e.g., "Ruban")
- **Category** (e.g., "Adhésifs")

Press Enter or click Search button

### Step 4: Select Material
Click the **"Select"** button on the material you want to update

### Step 5: Enter Quantity
1. Type the quantity to add
2. (Optional) Add reason: "Received order", "Inventory correction", etc.
3. Click **"Update Stock"**

✅ **Done!** Your stock is updated and a record is created automatically.

---

## 📋 What Gets Created

When you update stock, the system automatically:

| Item | Description |
|------|-------------|
| **Material Record** | Updates current_stock value |
| **Stock Movement** | Creates audit trail with: user, quantity, reason, timestamp |
| **Last Restocked Date** | Updated automatically |
| **User Record** | Logged with your user ID |

---

## 🔍 Search Tips

| Query | Finds |
|-------|-------|
| `293` | Code exact match or starts with |
| `Ruban` | Any material with "Ruban" in name |
| `Adh` | Starts with "Adh" (case-insensitive) |
| `Jaune` | Partial name match |

> **Pro Tip**: Shorter searches are faster! "Adh" returns faster than "Adhésifs"

---

## ⚠️ Common Issues

| Problem | Solution |
|---------|----------|
| No results found | Try shorter search term or different field |
| Button not visible | Check your user role (Admin/Stock Agent only) |
| Update failed | Ensure quantity > 0 and material exists |
| Changes not visible | Refresh page (F5) to see updates |

---

## 📊 Stock Status Meanings

| Status | Color | Meaning | Action |
|--------|-------|---------|--------|
| **Normal** | 🟢 Green | Stock is adequate | None needed |
| **Warning** | 🟡 Yellow | Stock approaching limits | Review soon |
| **Critical** | 🔴 Red | Stock below minimum | Urgent reorder |

---

## 💡 When to Use This Feature

**✅ Use "Add Quantity" for:**
- Receiving new shipments of existing parts
- Inventory audit corrections  
- Restocking common materials
- Adding returned items back

**❌ Don't use for:**
- New spare parts (use "Add New Material" form)
- Removing stock (use returns)
- Changing supplier/price (use edit material)

---

## 🔐 Who Can Use This?

- ✅ **Admin** - Full access
- ✅ **Stock Agent** - Full access  
- ❌ Technician, Supervisor - No access

---

## 📱 Mobile Compatibility

- ✅ Works on tablets
- ⚠️ Small phones: difficult to use (recommend desktop)
- Mobile keyboard closes after search

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| **Enter** | Perform search |
| **Escape** | Close modal |
| **Tab** | Navigate fields |

---

## 📞 Need Help?

1. **Check Material Detail page** - View stock history
2. **Check Stock Alerts** - See current stock issues
3. **Review Movement History** - Audit trail of changes
4. **Contact Admin** - For role/permission issues

---

## 🎯 Example Scenarios

### Scenario 1: Received New Order
```
1. Click "Add Quantity"
2. Search: "293"
3. Select: "Ruban Jaune"
4. Quantity: 100
5. Reason: "Received order #PO-2024-001"
6. Update
Result: Stock increases from 85 to 185 units
```

### Scenario 2: Inventory Correction
```
1. Click "Add Quantity"
2. Search: "MAT-050"
3. Select the material
4. Quantity: 15
5. Reason: "Stock audit correction - found 15 extra units"
6. Update
Result: Corrected stock with audit trail
```

### Scenario 3: Restocking
```
1. Click "Add Quantity"
2. Search: "Oil"
3. Select the material
4. Quantity: 50
5. Reason: "Standard restock"
6. Update
Result: Stock updated with standard restock record
```

---

## ✨ Features at a Glance

| Feature | Details |
|---------|---------|
| **Smart Search** | Code, name, category searching |
| **Real-time Results** | Live search with 20 max results |
| **Stock Display** | Current stock and status shown |
| **Audit Trail** | All updates recorded with user/timestamp |
| **Error Handling** | User-friendly error messages |
| **Responsive Design** | Works on different screen sizes |
| **No Duplicates** | Updates existing, doesn't create copies |

---

## 📈 What Happens Behind the Scenes

```
User Action → Material found → Quantity validated → 
Stock updated → Movement recorded → Email logged → Done!
```

The system ensures data integrity with:
- Database transactions
- Automatic timestamps
- User authentication
- Role-based access control
- Audit trail creation

---

## 🔄 Integration with Other Features

This feature integrates with:
- **Stock Alerts** - Recalculates stock status
- **Material Detail** - Updates visible in history
- **Movement History** - New record appears in list
- **Reports** - Included in stock reports
- **Email Notifications** - Optional alerts on updates

---

**Last Updated**: 2024
**Version**: 1.0
**Status**: Production Ready ✅

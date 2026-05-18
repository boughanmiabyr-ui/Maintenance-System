# Conditional Preventive Maintenance - Technician Quick Start Guide

## What is Conditional Preventive Maintenance?

Conditional Preventive Maintenance (CPM) is a maintenance strategy that monitors your equipment's actual condition and operation. Instead of maintaining on a fixed schedule, maintenance is performed when the machine reaches specific thresholds or shows signs of wear.

**Example**: Instead of servicing a machine every month (regardless of usage), CPM says: "Service this machine when it reaches 10,000 operating hours OR when an inspection shows wear patterns."

---

## How to Create a Conditional Maintenance Report

### Quick Steps:

#### 1. **Access the Wizard**
   - From Dashboard → Click **"New Maintenance Report"** button
   - OR Direct URL: `/new-maintenance-report`

#### 2. **Step 1: Select Your Zone**
   - Choose the production zone where the equipment is located
   - Example: "Zone A - Assembly", "Zone B - Cutting"

#### 3. **Step 2: Select Machine(s)**
   - Check the box next to the machine(s) you want to report on
   - Click **"Proceed to Category Selection"**

#### 4. **Step 3: Select Category**
   - Choose between:
     - **Corrective Maintenance** (for breakdowns/repairs)
     - **Preventive Maintenance** (for planned inspections)
   - Click **"Preventive Maintenance"**

#### 5. **Step 4: Select Preventive Type** ⭐ YOUR OPTION
   Choose one of three types:
   
   | Type | Use When |
   |------|----------|
   | **Systematic** | Regular monthly or semi-annual service |
   | **🎯 Conditional** | Equipment reaches operation counter threshold |
   | **Predictive** | Using sensor data and analytics |
   
   - Click **"Conditional Preventive Maintenance"**

#### 6. **Review Summary**
   - Verify Zone, Machine, and Type are correct
   - Click **"Start Conditional Maintenance"** button

---

## The 7-Step Conditional Maintenance Form

Once you click "Start," you'll complete a detailed inspection form with 7 steps:

### Step 1️⃣: Identification
**Record basic information:**
- Your name (technician)
- Date of inspection
- Machine type (KOMAX 355, PS9550, etc.)
- Machine zone/workstation
- Machine SAP code
- Operation counter reading

### Step 2️⃣: État Général (General Machine Condition)
**Inspect overall condition - Mark OK/NOK/N/A:**
- ✓ Machine clean and well-maintained
- ✓ No visual anomalies (leaks, cracks, corrosion)
- ✓ No abnormal vibrations
- ✓ No abnormal noises
- ✓ No cutting residue buildup

### Step 3️⃣: Lames & Caméra (Blades & Camera)
**Detailed blade inspection:**
- ✓ Blade general condition
- ✓ Blade wear progression
- ✓ Presence of cracks
- ✓ Presence of chips
- ✓ Blade alignment
- ✓ Blade deformation
- ✓ USB camera inspection completed
- ✓ Cutting edge status

**💡 Tip**: Use the camera verification for hard-to-see components. Click the "Photo" button to attach images.

### Step 4️⃣: Dénudage & Bloc (Stripping & Blade Block)
**Check stripping mechanism and blade assembly:**
- ✓ Knife position correct
- ✓ Vertical movement smooth
- ✓ Stripping quality acceptable
- ✓ Residue removal functioning
- ✓ Mechanism operating smoothly
- ✓ Blade block mounting secure
- ✓ All bolts properly tightened
- ✓ No mechanical play
- ✓ Component positioning correct
- ✓ Functional test passed

### Step 5️⃣: Nettoyage & Anomalies (Cleaning & Anomalies)
**Verify cleaning and detect issues:**
- ✓ Machine cleaned thoroughly
- ✓ Area secured (no loose parts)
- ✓ All debris removed
- ✓ Machine ready for production

**🚨 Anomaly Detection:**
If you found any issues, check **"Anomaly Detected"** and:
- Select criticality level:
  - 🟢 **Basse** (Low) - Can monitor
  - 🟡 **Moyenne** (Medium) - Schedule service soon
  - 🟠 **Haute** (High) - Service needed this week
  - 🔴 **Critique** (Critical) - Stop and fix immediately
- Describe what you found

### Step 6️⃣: Actions (Corrective Actions Taken)
**Record what you did:**
- ✓ Adjustment performed
- ✓ Blades replaced
- ✓ Cutting head adjusted
- ✓ Escalation to maintenance required
- Spare parts used (list them)

### Step 7️⃣: Résumé (Summary & Sign-Off)
**Review and finalize:**
- Summary shows your inspection results
- Number of OK checks
- Number of NOK checks
- Any anomalies found
- Correction actions taken

**Sign-off:**
- Enter your full name as technician
- Enter supervisor/team lead name

---

## Understanding Your Report Results

After completion, you'll see a summary showing:

| Metric | Meaning |
|--------|---------|
| **Contrôles OK** | Equipment aspects that passed inspection |
| **Contrôles NOK** | Equipment aspects that need attention |
| **Total effectués** | Total checks completed |

### Example:
```
✅ Contrôles OK:      22
⚠️  Contrôles NOK:     3
📊 Total effectués:    27
🚨 Anomalie détectée: Moyenne
```

This means the machine is mostly fine, but 3 items need attention (Medium priority).

---

## What Happens Next?

### For You (Technician):
✅ Your report is saved to the system
✅ A success message confirms submission
✅ You can create another report

### For Your Supervisor:
📧 Receives an email with:
- Your complete report
- PDF attachment with all details
- Inspection results
- Any anomalies detected
- Recommended actions

### For the Company:
📊 Report is archived for:
- Maintenance history tracking
- Equipment performance analysis
- Preventive maintenance planning
- Compliance documentation

---

## Tips & Best Practices

### Before You Start ✅
- [ ] Have the machine's SAP code ready
- [ ] Read the current operation counter
- [ ] Gather any materials needed (USB camera if available)
- [ ] Plan for ~30-45 minutes to complete inspection

### While Inspecting 🔍
- [ ] Take your time - thorough inspection prevents breakdowns
- [ ] If unsure about a check, mark it "N/A" rather than guessing
- [ ] Use the "Photo" button to document issues
- [ ] Be specific in descriptions - don't just say "bad," explain what's wrong
- [ ] Note the counter reading exactly

### After Completion ✅
- [ ] Double-check all required fields are filled
- [ ] Review your answers before submitting
- [ ] Verify supervisor name is spelled correctly
- [ ] Ensure signatures section is complete

---

## Troubleshooting

### "I can't find the Conditional Preventive Maintenance button"
**Solution**: Make sure you selected "Preventive Maintenance" in Step 3, then look for it in Step 4.

### "The form won't submit"
**Solution**: Check that you entered:
- Your name (technician field)
- Machine type
- Both signature fields

### "I need to change my answer"
**Solution**: You can click back through steps to navigate back to any previous section and modify your answers.

### "I don't understand a check item"
**Solution**: 
- Hover over the item name for more details
- If it doesn't apply to your machine, mark it "N/A"
- Leave remarks explaining why it's N/A

### "Where's my report after I submit?"
**Solution**: 
- It's saved automatically
- Supervisor gets an email with PDF
- You can view history in "View Reports"

---

## Key Controls & Buttons

| Button/Control | Action |
|---|---|
| **✓ OK** | Check passed inspection |
| **✗ NOK** | Check failed - needs attention |
| **N/A** | Not applicable to this machine |
| **Photo** | Attach photo to documentation |
| **📷 Camera** | USB camera verification |
| **Previous** | Go to previous step |
| **Next** | Go to next step |
| **Submit** | Finalize and send report |

---

## Report Format (What Supervisor Sees)

Your completed report includes:

**Header Section:**
- SEBN TN — Service Maintenance
- Report reference number
- Date and time

**Main Sections:**
- Technician identification
- Machine information (Type, Zone, SAP Code, Counter)
- All 27 inspection check results
- Anomaly details (if any)
- Corrective actions taken
- Final summary with statistics
- Digital signatures

**Attachment:**
- PDF version for printing/archiving

---

## Integration with Other Systems

### Counter Reset (After Maintenance)
If you perform maintenance and reset the counter:
1. Route: `/preventive-maintenance/conditional/reset`
2. Select machine
3. Record counter reading before reset
4. Submit

### Component Replacement (After Maintenance)
If you replace components:
1. Route: `/preventive-maintenance/conditional/replace`
2. Select machine
3. List components replaced
4. Counter is automatically reset

---

## Frequently Asked Questions (FAQ)

**Q: How long should an inspection take?**
A: Typically 30-45 minutes including notes and photos.

**Q: Can I save and resume later?**
A: The form saves automatically. Close and come back anytime.

**Q: What if the machine is down?**
A: You can still inspect it. Mark NOK checks appropriately.

**Q: Who receives my report?**
A: Your direct supervisor via email with PDF attachment.

**Q: Can I attach multiple photos?**
A: Yes, click "Photo" for each item you want to document.

**Q: What does "escalation required" mean?**
A: It means the issue needs supervisor/engineer review - not a routine fix.

**Q: Is this report backed up?**
A: Yes, permanently stored in the database. Supervisor also has email copy.

**Q: What if I make a mistake?**
A: Submit it anyway. Supervisor can add notes or request resubmission.

---

## Next Steps

1. **First Use**: Ask your supervisor to walk through one report with you
2. **Practice**: Complete a few reports with supervisor review
3. **Independent**: After 3-5 reports, you'll be confident doing them alone
4. **Continuous**: Each report helps build machine maintenance history

---

**Need Help?**
Contact your supervisor or maintenance coordinator for additional guidance.

**Last Updated**: May 16, 2026
**Version**: 1.0

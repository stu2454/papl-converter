# Fixing Empty Support Category and Registration Group

## Problem

When converting the Support Catalogue, some fields come back empty:
- `"support_category": ""`
- `"registration_group": ""`

## Root Cause

The Excel file has different column names than expected. The converter looks for exact column names like "Support Category" but your Excel might have:
- Different spelling/capitalization
- Extra spaces
- Different terminology (e.g., "Support Purpose" instead of "Support Category")

## Solution - Use the New Configuration Page

### Step 1: Upload Files

Upload your PAPL and Support Catalogue as usual.

### Step 2: Go to "Configure Conversion" Page

This NEW page shows:
1. All columns in your Excel file
2. Auto-detected column mapping
3. Manual override options

### Step 3: Review Auto-Detection

The page will show which columns it found:

```
✅ Item Number: Support Item Number
✅ Item Name: Support Item Name  
⚠️ Category: NOT FOUND
⚠️ Registration: NOT FOUND
✅ Unit: Unit
```

### Step 4: Manual Mapping (if needed)

If auto-detection failed, use the dropdown menus to select the correct columns:

**Example:**
- If your Excel has "Support Purpose" → Select it for "Support Category"
- If your Excel has "Provider Group" → Select it for "Registration Group"

### Step 5: Save Mapping

Click "💾 Save Column Mapping"

### Step 6: Run Conversion

Go to "Run Conversion" and the converter will use your manual mapping!

## Updated Converter Features

### Improved Auto-Detection

The converter now looks for many variations:

**Support Category:**
- "Support Category"
- "Category"
- "Support Purpose"
- "Purpose"

**Registration Group:**
- "Registration Group"
- "Registration"
- "Provider Registration"
- "Rego Group"
- "Provider Group"

**Support Item Number:**
- "Support Item Number"
- "Item Number"
- "Support Item No"
- "Item No"
- "Support Item"

**Support Item Name:**
- "Support Item Name"
- "Item Name"
- "Support Item Description"
- "Description"
- "Name"

**Unit:**
- "Unit"
- "Unit of Measure"
- "UOM"
- "Unit of Delivery"

**Quote Required:**
- "Quote Required"
- "Quote"
- "Quotation Required"
- "Price Control"

### Metadata Tracking

Each converted item now includes column mapping metadata:

```json
{
  "support_item_number": "05_120603831_0103_1_2",
  "metadata": {
    "columns_found": {
      "item_number": "Support Item Number",
      "item_name": "Support Item Name",
      "category": "Support Purpose",     ← Shows what column was used
      "registration": "Provider Group",  ← Shows what column was used
      "unit": "Unit",
      "quote": "Quote Required"
    }
  }
}
```

This helps you verify the correct columns were used!

## Verifying the Fix

### Before (Empty Fields)

```json
{
  "support_item_number": "05_120603831_0103_1_2",
  "support_item_name": "Standing and/or Walking Frame - Child",
  "support_category": "",           ← EMPTY
  "registration_group": "",         ← EMPTY
  "unit": "E"
}
```

### After (Filled Fields)

```json
{
  "support_item_number": "05_120603831_0103_1_2",
  "support_item_name": "Standing and/or Walking Frame - Child",
  "support_category": "Assistive Technology",  ← FILLED
  "registration_group": "Assistive Technology",← FILLED
  "unit": "E"
}
```

## Quick Diagnostic

### Check Your Excel Column Names

1. Open your Support Catalogue in Excel
2. Look at the first row (header row)
3. Note the exact column names for:
   - Support category/purpose
   - Registration/provider group

### Common Excel Variations

| Your Excel Might Say | Converter Expects |
|---------------------|-------------------|
| Support Purpose | Support Category |
| Provider Group | Registration Group |
| Registration Type | Registration Group |
| Item Description | Support Item Name |
| UOM | Unit |

### If Columns Still Don't Map

1. Take a screenshot of your Excel headers
2. Use the manual mapping dropdowns
3. Select the exact column name from your Excel
4. Save mapping
5. Run conversion

## Testing the Fix

After running the conversion:

1. Go to "View Results"
2. Click on "JSON Data"
3. Expand a support item
4. Check the `metadata.columns_found` section
5. Verify it shows the correct source columns

Example verification:
```json
"metadata": {
  "columns_found": {
    "category": "Support Purpose",  ← Should match your Excel
    "registration": "Provider Registration Group"  ← Should match your Excel
  }
}
```

## Still Having Issues?

### Debug Steps

1. **View Sample Data** in Configure Conversion page
   - Check if data appears in the preview table
   - Verify category and registration columns have values

2. **Check for Merged Cells**
   - Excel shouldn't have merged header cells
   - Each column should have one clear name

3. **Check for Hidden Characters**
   - Column names might have trailing spaces
   - The converter now handles this automatically

4. **Check Sheet Selection**
   - Data must be in the first worksheet
   - Move data to first sheet if needed

## Package Version

This fix is included in:
- ✅ `papl_converter_app_PORT8502.zip` (includes fix)
- ✅ New "Configure Conversion" page added
- ✅ Improved auto-detection
- ✅ Manual column mapping
- ✅ Metadata tracking

## Need More Help?

The "Configure Conversion" page shows:
- All your Excel columns
- Which ones were auto-detected
- Manual override options
- Sample data preview

Use this to diagnose and fix column mapping issues before running the conversion!

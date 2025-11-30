"""
Page 2: Configure Conversion & Diagnose Columns
Check Excel column names and configure conversion
"""

import streamlit as st
import pandas as pd
import io
from pathlib import Path

# NDIA Brand Colors
NDIA_BLUE = "#003087"
NDIA_ACCENT = "#00B5E2"

st.title("⚙️ Configure Conversion")
st.markdown("### Review Excel Structure & Configure Options")

# Check if catalogue is uploaded
if not st.session_state.get('catalogue_uploaded'):
    st.warning("⚠️ Please upload the Support Catalogue first in 'Upload Inputs' page")
    st.stop()

# Analyze Excel columns
st.markdown("## 📊 Excel Column Analysis")

catalogue_file = st.session_state.uploaded_files['catalogue']

try:
    # Read Excel to analyze structure
    df = pd.read_excel(io.BytesIO(catalogue_file.read()), sheet_name=0, nrows=10)
    catalogue_file.seek(0)
    
    st.success(f"✅ Loaded {len(df)} sample rows")
    
    # Show all column names
    st.markdown("### Detected Column Names")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**All Columns:**")
        for i, col in enumerate(df.columns):
            st.write(f"{i+1}. `{col}`")
    
    with col2:
        st.markdown("**Column Mapping Detection:**")
        
        # Auto-detect columns
        def find_column(possible_names):
            for col in df.columns:
                col_lower = str(col).lower().strip()
                for possible in possible_names:
                    if possible.lower() in col_lower:
                        return col
            return None
        
        item_number_col = find_column(['Support Item Number', 'Item Number', 'Support Item No', 'Item No', 'Support Item'])
        item_name_col = find_column(['Support Item Name', 'Item Name', 'Support Item Description', 'Description', 'Name'])
        category_col = find_column(['Support Category', 'Category', 'Support Purpose', 'Purpose'])
        registration_col = find_column(['Registration Group', 'Registration', 'Provider Registration', 'Rego Group', 'Provider Group'])
        unit_col = find_column(['Unit', 'Unit of Measure', 'UOM', 'Unit of Delivery'])
        quote_col = find_column(['Quote Required', 'Quote', 'Quotation Required', 'Price Control'])
        
        st.write(f"✅ Item Number: `{item_number_col}`" if item_number_col else "❌ Item Number: NOT FOUND")
        st.write(f"✅ Item Name: `{item_name_col}`" if item_name_col else "❌ Item Name: NOT FOUND")
        st.write(f"✅ Category: `{category_col}`" if category_col else "⚠️ Category: NOT FOUND")
        st.write(f"✅ Registration: `{registration_col}`" if registration_col else "⚠️ Registration: NOT FOUND")
        st.write(f"✅ Unit: `{unit_col}`" if unit_col else "⚠️ Unit: NOT FOUND")
        st.write(f"✅ Quote: `{quote_col}`" if quote_col else "⚠️ Quote: NOT FOUND")
    
    # Show sample data
    st.markdown("---")
    st.markdown("### Sample Data (First 5 Rows)")
    st.dataframe(df.head(), use_container_width=True)
    
    # Manual column mapping
    st.markdown("---")
    st.markdown("## 🔧 Manual Column Mapping (if needed)")
    
    st.info("If auto-detection failed, manually map the columns below:")
    
    all_columns = [''] + list(df.columns)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        manual_item_number = st.selectbox("Support Item Number", all_columns, 
            index=all_columns.index(item_number_col) if item_number_col in all_columns else 0)
        manual_category = st.selectbox("Support Category", all_columns,
            index=all_columns.index(category_col) if category_col in all_columns else 0)
    
    with col2:
        manual_item_name = st.selectbox("Support Item Name", all_columns,
            index=all_columns.index(item_name_col) if item_name_col in all_columns else 0)
        manual_registration = st.selectbox("Registration Group", all_columns,
            index=all_columns.index(registration_col) if registration_col in all_columns else 0)
    
    with col3:
        manual_unit = st.selectbox("Unit", all_columns,
            index=all_columns.index(unit_col) if unit_col in all_columns else 0)
        manual_quote = st.selectbox("Quote Required", all_columns,
            index=all_columns.index(quote_col) if quote_col in all_columns else 0)
    
    # Save mapping to session state
    if st.button("💾 Save Column Mapping", type="primary"):
        st.session_state.column_mapping = {
            'item_number': manual_item_number if manual_item_number else item_number_col,
            'item_name': manual_item_name if manual_item_name else item_name_col,
            'category': manual_category if manual_category else category_col,
            'registration': manual_registration if manual_registration else registration_col,
            'unit': manual_unit if manual_unit else unit_col,
            'quote': manual_quote if manual_quote else quote_col
        }
        st.success("✅ Column mapping saved! Proceed to 'Run Conversion'")
        
        # Show what will be used
        with st.expander("View Saved Mapping"):
            st.json(st.session_state.column_mapping)
    
    # Conversion options
    st.markdown("---")
    st.markdown("## ⚙️ Conversion Options")
    
    st.session_state.convert_catalogue = st.checkbox("Convert Support Catalogue to JSON", value=True)
    st.session_state.convert_rules = st.checkbox("Convert Claiming Rules to YAML", value=True)
    st.session_state.convert_guidance = st.checkbox("Convert Guidance to Markdown", value=True)
    
    st.session_state.validate_pricing = st.checkbox("Validate State Pricing", value=True)
    st.session_state.validate_rules = st.checkbox("Validate Business Rules", value=True)
    st.session_state.check_nt_loading = st.checkbox("Check NT Remote Loading", value=True)
    
    st.markdown("---")
    st.info("✅ Configuration complete! Go to **'Run Conversion'** to process the files.")

except Exception as e:
    st.error(f"Error analyzing Excel file: {str(e)}")
    st.exception(e)

# Help section
with st.expander("ℹ️ Understanding Column Detection"):
    st.markdown("""
### How Column Detection Works

The converter looks for columns containing these keywords:

**Support Item Number:**
- "Support Item Number", "Item Number", "Support Item No", "Item No"

**Support Item Name:**
- "Support Item Name", "Item Name", "Description"

**Support Category:**
- "Support Category", "Category", "Support Purpose", "Purpose"

**Registration Group:**
- "Registration Group", "Registration", "Provider Registration"

**Unit:**
- "Unit", "Unit of Measure", "UOM"

**Quote Required:**
- "Quote Required", "Quote", "Quotation Required"

### If Columns Aren't Found

Use the manual column mapping above to select the correct columns from your Excel file.

### Common Issues

1. **Extra spaces in column names** - The detector handles this
2. **Different terminology** - Use manual mapping
3. **Multiple worksheets** - Make sure data is in first sheet
4. **Merged header rows** - Excel should have clean single-row headers
""")

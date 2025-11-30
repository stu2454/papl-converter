"""
Page 3: Run Conversion
Execute the PAPL to digital-first transformation
"""

import streamlit as st
import sys
import io
from pathlib import Path

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))

from converter import PAPLConverter

# NDIA Brand Colors
NDIA_BLUE = "#003087"
NDIA_ACCENT = "#00B5E2"

st.title("🔄 Run Conversion")
st.markdown("### Transform PAPL to Digital-First Formats")

# Check if files are uploaded
if not st.session_state.get('papl_uploaded') and not st.session_state.get('catalogue_uploaded'):
    st.warning("⚠️ Please upload files first in the 'Upload Inputs' page")
    st.stop()

# Initialize converter
if 'converter' not in st.session_state or st.session_state.converter is None:
    st.session_state.converter = PAPLConverter()

# Conversion options
st.markdown("## Conversion Options")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### What to Convert")
    convert_catalogue = st.checkbox("Convert Support Catalogue to JSON", value=True,
                                   help="Extract pricing data into structured JSON format")
    convert_rules = st.checkbox("Convert Claiming Rules to YAML", value=True,
                               help="Extract business rules into validated YAML")
    convert_guidance = st.checkbox("Convert Guidance to Markdown", value=True,
                                  help="Convert explanatory content to accessible Markdown")

with col2:
    st.markdown("### Validation Options")
    validate_pricing = st.checkbox("Validate State Pricing", value=True,
                                  help="Check for inconsistencies in state-by-state pricing")
    validate_rules = st.checkbox("Validate Business Rules", value=True,
                                help="Ensure rules are complete and consistent")
    check_nt_loading = st.checkbox("Check NT Remote Loading", value=True,
                                  help="Verify NT prices are 6% higher than other states")

# Run conversion
st.markdown("---")

if st.button("🚀 Start Conversion", type="primary", use_container_width=True):
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Load files
        status_text.text("Loading PAPL document...")
        progress_bar.progress(10)
        
        if st.session_state.get('papl_uploaded'):
            papl_file = st.session_state.uploaded_files['papl']
            st.session_state.converter.load_papl_document(io.BytesIO(papl_file.read()))
            papl_file.seek(0)
        
        # Step 2: Load catalogue
        status_text.text("Loading Support Catalogue...")
        progress_bar.progress(20)
        
        if st.session_state.get('catalogue_uploaded'):
            catalogue_file = st.session_state.uploaded_files['catalogue']
            st.session_state.converter.load_support_catalogue(io.BytesIO(catalogue_file.read()))
            catalogue_file.seek(0)
        
        # Step 3: Convert to JSON
        if convert_catalogue and st.session_state.get('catalogue_uploaded'):
            status_text.text("Converting Support Catalogue to JSON...")
            progress_bar.progress(40)
            
            # Get column mapping if available
            column_mapping = st.session_state.get('column_mapping', None)
            
            json_output = st.session_state.converter.convert_catalogue_to_json(column_mapping)
            st.session_state.json_output = json_output
            
            st.success(f"✅ Converted {len(json_output.get('support_items', []))} support items to JSON")
            
            # Show column mapping used
            if json_output.get('support_items') and len(json_output['support_items']) > 0:
                first_item = json_output['support_items'][0]
                if 'metadata' in first_item and 'columns_found' in first_item['metadata']:
                    with st.expander("View Column Mapping Used"):
                        st.json(first_item['metadata']['columns_found'])
        
        # Step 4: Convert to YAML
        if convert_rules and st.session_state.get('papl_uploaded'):
            status_text.text("Converting claiming rules to YAML...")
            progress_bar.progress(60)
            
            yaml_output = st.session_state.converter.convert_claiming_rules_to_yaml()
            st.session_state.yaml_output = yaml_output
            
            rule_count = len(yaml_output.get('claiming_rules', {}))
            st.success(f"✅ Converted {rule_count} claiming rule sections to YAML")
        
        # Step 5: Convert to Markdown
        if convert_guidance and st.session_state.get('papl_uploaded'):
            status_text.text("Converting guidance to Markdown...")
            progress_bar.progress(75)
            
            markdown_output = st.session_state.converter.convert_guidance_to_markdown()
            st.session_state.markdown_output = markdown_output
            
            st.success(f"✅ Converted guidance to Markdown ({len(markdown_output)} characters)")
        
        # Step 6: Validation
        status_text.text("Running validation checks...")
        progress_bar.progress(90)
        
        validation_errors = st.session_state.converter.validate_conversion()
        st.session_state.validation_errors = validation_errors
        
        # Step 7: Export files
        status_text.text("Exporting output files...")
        progress_bar.progress(95)
        
        output_dir = Path("/home/claude/papl_converter/outputs")
        output_files = st.session_state.converter.export_all_formats(output_dir)
        st.session_state.output_files = output_files
        st.session_state.output_count = len(output_files)
        
        # Complete
        progress_bar.progress(100)
        status_text.text("Conversion complete!")
        
        st.session_state.conversion_complete = True
        
        # Summary
        st.markdown("---")
        st.markdown("## ✅ Conversion Complete!")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("JSON Files", "1" if convert_catalogue else "0")
            if convert_catalogue:
                st.caption(f"{len(st.session_state.json_output.get('support_items', []))} support items")
        
        with col2:
            st.metric("YAML Files", "1" if convert_rules else "0")
            if convert_rules:
                rule_count = len(st.session_state.yaml_output.get('claiming_rules', {}))
                st.caption(f"{rule_count} claiming rules")
        
        with col3:
            st.metric("Markdown Files", "1" if convert_guidance else "0")
            if convert_guidance:
                char_count = len(st.session_state.markdown_output)
                st.caption(f"{char_count:,} characters")
        
        # Validation summary
        if validation_errors:
            error_count = len([e for e in validation_errors if e['severity'] == 'error'])
            warning_count = len([e for e in validation_errors if e['severity'] == 'warning'])
            
            st.markdown("### Validation Results")
            
            col1, col2 = st.columns(2)
            col1.metric("Errors Found", error_count, delta=f"-{error_count}" if error_count else "0", delta_color="inverse")
            col2.metric("Warnings", warning_count)
            
            if error_count > 0:
                st.warning(f"⚠️ Found {error_count} errors that need attention")
            else:
                st.success("✅ No critical errors found!")
            
            with st.expander("View Validation Details"):
                for error in validation_errors[:10]:  # Show first 10
                    severity_emoji = "🔴" if error['severity'] == 'error' else "🟡"
                    st.write(f"{severity_emoji} **{error['type']}**: {error.get('message', error.get('item', 'Unknown'))}")
        
        # Next steps
        st.markdown("### Next Steps")
        st.info("""
**Explore Your Results:**
1. 📊 **View Results** - Browse JSON, YAML, and Markdown outputs
2. ✅ **Validation Report** - See detailed validation findings
3. 🔍 **Before/After Comparison** - Compare original vs converted
4. 🌐 **Multi-Framework Demo** - See Old vs New Framework views
5. 📦 **Export Package** - Download all converted files
        """)
        
    except Exception as e:
        st.error(f"❌ Conversion failed: {str(e)}")
        st.exception(e)
        progress_bar.progress(0)
        status_text.text("")

# Show current status
elif st.session_state.get('conversion_complete'):
    st.success("✅ Conversion previously completed")
    
    st.markdown("### Converted Files")
    
    if st.session_state.get('output_files'):
        for format_type, file_path in st.session_state.output_files.items():
            st.write(f"📄 **{format_type.upper()}**: `{file_path.name}`")
    
    st.info("Navigate to other pages to explore results or click button above to re-run conversion")

else:
    st.info("👆 Click 'Start Conversion' to begin transforming your PAPL documents")
    
    # Show what will be converted
    st.markdown("### Ready to Convert:")
    
    items = []
    if st.session_state.get('catalogue_uploaded') and convert_catalogue:
        cat_rows = st.session_state.file_analysis.get('catalogue', {}).get('rows', 0) - 1
        items.append(f"📊 **{cat_rows:,}** support items → JSON")
    
    if st.session_state.get('papl_uploaded') and convert_rules:
        items.append(f"📋 **Claiming rules** → YAML")
    
    if st.session_state.get('papl_uploaded') and convert_guidance:
        items.append(f"📝 **Guidance sections** → Markdown")
    
    for item in items:
        st.write(item)

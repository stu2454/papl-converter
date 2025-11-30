"""
Page 4: View Results
Browse and explore converted outputs
"""

import streamlit as st
import json
import yaml
from pathlib import Path

# NDIA Brand Colors
NDIA_BLUE = "#003087"
NDIA_ACCENT = "#00B5E2"

st.title("📊 View Results")
st.markdown("### Explore Your Converted Digital-First Formats")

# Check if conversion is complete
if not st.session_state.get('conversion_complete'):
    st.warning("⚠️ Please run the conversion first in the 'Run Conversion' page")
    st.stop()

# Tabs for different outputs
tab1, tab2, tab3, tab4 = st.tabs(["📄 JSON Data", "📋 YAML Rules", "📝 Markdown Guidance", "📦 All Files"])

with tab1:
    st.markdown("## JSON Pricing Data")
    st.markdown("Structured, validated, machine-readable pricing information")
    
    if st.session_state.get('json_output'):
        json_data = st.session_state.json_output
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        
        total_items = len(json_data.get('support_items', []))
        col1.metric("Total Support Items", f"{total_items:,}")
        
        # Count items with complete state pricing
        complete_pricing = sum(1 for item in json_data.get('support_items', []) 
                              if len(item.get('price_limits', {})) == 8)
        col2.metric("Complete State Pricing", f"{complete_pricing:,}")
        
        # Count items requiring quotes
        quote_required = sum(1 for item in json_data.get('support_items', []) 
                           if item.get('quote_required', False))
        col3.metric("Quote Required Items", f"{quote_required:,}")
        
        # Display options
        st.markdown("### Explore Data")
        
        display_option = st.radio(
            "View:", 
            ["Sample Items", "Full JSON", "Search"],
            horizontal=True
        )
        
        if display_option == "Sample Items":
            num_items = st.slider("Number of items to show", 1, 20, 5)
            
            for i, item in enumerate(json_data.get('support_items', [])[:num_items]):
                with st.expander(f"{item.get('support_item_number', 'Unknown')} - {item.get('support_item_name', 'Unknown')}"):
                    st.json(item)
        
        elif display_option == "Full JSON":
            st.json(json_data)
        
        else:  # Search
            search_term = st.text_input("Search support items", placeholder="e.g., Occupational Therapy")
            
            if search_term:
                matching_items = [
                    item for item in json_data.get('support_items', [])
                    if search_term.lower() in item.get('support_item_name', '').lower()
                    or search_term.lower() in item.get('support_item_number', '').lower()
                ]
                
                st.write(f"Found {len(matching_items)} matching items")
                
                for item in matching_items[:10]:
                    with st.expander(f"{item.get('support_item_number')} - {item.get('support_item_name')}"):
                        st.json(item)
        
        # Download button
        st.markdown("---")
        json_str = json.dumps(json_data, indent=2)
        st.download_button(
            label="📥 Download JSON",
            data=json_str,
            file_name="support_catalogue.json",
            mime="application/json"
        )
    
    else:
        st.info("No JSON output available. Ensure Support Catalogue conversion was enabled.")

with tab2:
    st.markdown("## YAML Business Rules")
    st.markdown("Structured, testable claiming rules and conditions")
    
    if st.session_state.get('yaml_output'):
        yaml_data = st.session_state.yaml_output
        
        # Summary
        rule_count = len(yaml_data.get('claiming_rules', {}))
        st.metric("Claiming Rule Sections", rule_count)
        
        # List rules
        st.markdown("### Available Rules")
        
        for rule_name, rule_data in yaml_data.get('claiming_rules', {}).items():
            with st.expander(f"📋 {rule_data.get('section_title', rule_name)}"):
                st.markdown(f"**Rule Key:** `{rule_name}`")
                
                if rule_data.get('conditions'):
                    st.markdown("**Conditions:**")
                    for condition in rule_data['conditions']:
                        st.write(f"- {condition}")
                
                st.markdown("**YAML Structure:**")
                st.code(yaml.dump({rule_name: rule_data}, default_flow_style=False), language="yaml")
        
        # Download button
        st.markdown("---")
        yaml_str = yaml.dump(yaml_data, default_flow_style=False, sort_keys=False)
        st.download_button(
            label="📥 Download YAML",
            data=yaml_str,
            file_name="claiming_rules.yaml",
            mime="application/x-yaml"
        )
    
    else:
        st.info("No YAML output available. Ensure claiming rules conversion was enabled.")

with tab3:
    st.markdown("## Markdown Guidance")
    st.markdown("Human-readable explanatory content")
    
    if st.session_state.get('markdown_output'):
        markdown_text = st.session_state.markdown_output
        
        # Stats
        char_count = len(markdown_text)
        word_count = len(markdown_text.split())
        line_count = len(markdown_text.split('\n'))
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Characters", f"{char_count:,}")
        col2.metric("Words", f"{word_count:,}")
        col3.metric("Lines", f"{line_count:,}")
        
        # Display options
        display_mode = st.radio("View as:", ["Rendered", "Source"], horizontal=True)
        
        if display_mode == "Rendered":
            st.markdown(markdown_text)
        else:
            st.code(markdown_text, language="markdown")
        
        # Download
        st.markdown("---")
        st.download_button(
            label="📥 Download Markdown",
            data=markdown_text,
            file_name="papl_guidance.md",
            mime="text/markdown"
        )
    
    else:
        st.info("No Markdown output available. Ensure guidance conversion was enabled.")

with tab4:
    st.markdown("## All Output Files")
    
    if st.session_state.get('output_files'):
        output_files = st.session_state.output_files
        
        st.markdown("### Generated Files")
        
        for format_type, file_path in output_files.items():
            file_path = Path(file_path)
            
            if file_path.exists():
                file_size = file_path.stat().st_size
                
                col1, col2, col3 = st.columns([2, 1, 1])
                col1.write(f"📄 **{format_type.upper()}**")
                col2.write(f"{file_size:,} bytes")
                
                with col3:
                    with open(file_path, 'r') as f:
                        file_content = f.read()
                    
                    st.download_button(
                        label="Download",
                        data=file_content,
                        file_name=file_path.name,
                        key=f"download_{format_type}"
                    )
        
        st.markdown("---")
        st.markdown("### Download All as ZIP")
        
        if st.button("📦 Create ZIP Package"):
            import zipfile
            import io
            
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for format_type, file_path in output_files.items():
                    file_path = Path(file_path)
                    if file_path.exists():
                        zip_file.write(file_path, file_path.name)
            
            st.download_button(
                label="📥 Download ZIP Package",
                data=zip_buffer.getvalue(),
                file_name="papl_digital_first_outputs.zip",
                mime="application/zip"
            )
    
    else:
        st.info("No output files available yet.")

# Comparison tool
st.markdown("---")
st.markdown("## 🔍 Quick Comparison")

if st.session_state.get('json_output'):
    st.markdown("### Find Support Item")
    
    search = st.text_input("Enter support item number or name", placeholder="e.g., 01_001_0117_1_3")
    
    if search:
        json_data = st.session_state.json_output
        matching = [
            item for item in json_data.get('support_items', [])
            if search.lower() in item.get('support_item_number', '').lower()
            or search.lower() in item.get('support_item_name', '').lower()
        ]
        
        if matching:
            item = matching[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Original Format (Conceptual)**")
                st.code(f"""
SUPPORT ITEM: {item.get('support_item_name')}
Number: {item.get('support_item_number')}
Category: {item.get('support_category')}

PRICING (Manual lookup in PDF table):
NSW: [lookup required]
VIC: [lookup required]
...
                """, language="text")
            
            with col2:
                st.markdown("**Digital-First Format (JSON)**")
                st.json(item)
        else:
            st.warning("No matching items found")

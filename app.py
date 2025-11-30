"""
PAPL to Digital-First Converter
Main application entry point
"""

import streamlit as st
import sys
import os

# NDIA Brand Colors
NDIA_BLUE = "#003087"
NDIA_LIGHT_BLUE = "#0066CC"
NDIA_ACCENT = "#00B5E2"

# Configure page
st.set_page_config(
    page_title="PAPL to Digital-First Converter",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown(f"""
<style>
.main-header {{
    background: linear-gradient(135deg, {NDIA_BLUE} 0%, {NDIA_LIGHT_BLUE} 100%);
    padding: 2rem;
    border-radius: 10px;
    color: white;
    margin-bottom: 2rem;
}}
.metric-card {{
    background-color: #F8F9FA;
    border-left: 5px solid {NDIA_ACCENT};
    padding: 15px;
    border-radius: 5px;
    margin: 10px 0;
}}
.success-box {{
    background-color: #D4EDDA;
    border-left: 5px solid #28A745;
    padding: 15px;
    border-radius: 5px;
    margin: 10px 0;
}}
.info-box {{
    background-color: #E8F4F8;
    border-left: 5px solid {NDIA_ACCENT};
    padding: 15px;
    border-radius: 5px;
    margin: 10px 0;
}}
.warning-box {{
    background-color: #FFF3CD;
    border-left: 5px solid #FFC107;
    padding: 15px;
    border-radius: 5px;
    margin: 10px 0;
}}
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown(f"""
<div class='main-header'>
<h1 style='color: white; margin: 0;'>🔄 PAPL to Digital-First Converter</h1>
<p style='color: white; margin: 10px 0 0 0; font-size: 18px;'>
Transform NDIS Pricing Arrangements from static documents to structured, validated, digital-first formats
</p>
</div>
""", unsafe_allow_html=True)

# Introduction
st.markdown("""
## Welcome to the PAPL Converter

This application demonstrates the digital-first transformation by converting actual PAPL content from:
- **Static formats** (Word documents, Excel spreadsheets, PDFs)
- **To digital-first formats** (JSON data, YAML rules, Markdown guidance)

### What This App Does

1. **📥 Input Processing** - Accepts Word PAPL (104 pages) and Excel Support Catalogue
2. **🔄 Intelligent Conversion** - Extracts and structures data, rules, and guidance
3. **✅ Validation** - Catches errors that static documents can't detect
4. **📊 Multi-Format Output** - Generates JSON, YAML, Markdown, and interactive views
5. **🔍 Comparison Tools** - Shows before/after and version differences
6. **🌐 Live Preview** - Demonstrates how same data serves multiple frameworks
""")

# Key features
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
<div class='metric-card'>
<h3 style='color: {NDIA_BLUE}; margin-top: 0;'>Input Formats</h3>
<ul>
<li>Word PAPL documents</li>
<li>Excel Support Catalogue</li>
<li>PDF price lists</li>
<li>Legacy spreadsheets</li>
</ul>
</div>
""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
<div class='metric-card'>
<h3 style='color: {NDIA_BLUE}; margin-top: 0;'>Output Formats</h3>
<ul>
<li>JSON (pricing data)</li>
<li>YAML (business rules)</li>
<li>Markdown (guidance)</li>
<li>Interactive web views</li>
</ul>
</div>
""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""
<div class='metric-card'>
<h3 style='color: {NDIA_BLUE}; margin-top: 0;'>Demonstrations</h3>
<ul>
<li>Validation engine</li>
<li>Version comparison</li>
<li>Multi-framework views</li>
<li>API preview</li>
</ul>
</div>
""", unsafe_allow_html=True)

# Quick start
st.markdown("---")
st.markdown("## Quick Start")

st.markdown("""
### Choose Your Path:

**Option 1: Full PAPL Conversion** *(Recommended for demonstration)*
- Upload your complete PAPL Word document
- Upload Support Catalogue Excel file
- Convert entire document to digital-first formats
- See comprehensive validation and comparison

**Option 2: Section-by-Section** *(Best for pilot)*
- Select specific PAPL sections
- Convert incrementally
- Focus on pilot-relevant content

**Option 3: Excel Catalogue Only** *(Quick start)*
- Upload Support Catalogue Excel
- Generate JSON pricing data
- See immediate validation benefits

Navigate using the sidebar →
""")

# Status indicators
st.markdown("---")
st.markdown("## Current Status")

# Initialize session state
if 'papl_uploaded' not in st.session_state:
    st.session_state.papl_uploaded = False
if 'catalogue_uploaded' not in st.session_state:
    st.session_state.catalogue_uploaded = False
if 'conversion_complete' not in st.session_state:
    st.session_state.conversion_complete = False

col1, col2, col3, col4 = st.columns(4)

with col1:
    status = "✅" if st.session_state.papl_uploaded else "⏳"
    st.metric("PAPL Upload", status)

with col2:
    status = "✅" if st.session_state.catalogue_uploaded else "⏳"
    st.metric("Catalogue Upload", status)

with col3:
    status = "✅" if st.session_state.conversion_complete else "⏳"
    st.metric("Conversion", status)

with col4:
    if st.session_state.conversion_complete:
        st.metric("Output Files", f"{st.session_state.get('output_count', 0)}")
    else:
        st.metric("Output Files", "0")

# Navigation guide
st.markdown("---")
st.markdown(f"""
<div class='info-box'>
<h3 style='margin-top: 0;'>Navigation Guide</h3>
<p><strong>Use the sidebar</strong> to navigate between different conversion stages:</p>
<ol>
<li><strong>Upload Inputs</strong> - Provide PAPL Word doc and Excel catalogue</li>
<li><strong>Configure Conversion</strong> - Select sections, validation rules, output formats</li>
<li><strong>Run Conversion</strong> - Execute the transformation</li>
<li><strong>View Results</strong> - Explore JSON, YAML, Markdown outputs</li>
<li><strong>Validation Report</strong> - See errors caught and fixed</li>
<li><strong>Before/After Comparison</strong> - Visual side-by-side comparison</li>
<li><strong>Multi-Framework Demo</strong> - See Old vs New Framework views</li>
<li><strong>API Preview</strong> - Test live API responses</li>
<li><strong>Export Package</strong> - Download all converted files</li>
</ol>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; padding: 20px; background-color: {NDIA_BLUE}; border-radius: 10px; color: white;'>
<p style='margin: 0;'><strong>NDIA Markets Delivery - Digital-First Pricing Transformation</strong></p>
<p style='margin: 5px 0 0 0; font-size: 14px;'>Demonstrating structured data, validated rules, and accessible guidance</p>
</div>
""", unsafe_allow_html=True)

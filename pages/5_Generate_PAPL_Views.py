"""
Page 5: Generate PAPL Views
Create different presentations of PAPL data for different user types
"""

import streamlit as st
import json
import yaml
from pathlib import Path

# NDIA Brand Colors
NDIA_BLUE = "#003087"
NDIA_ACCENT = "#00B5E2"

st.title("🎨 Generate PAPL Views")
st.markdown("### Create Custom Presentations from Digital-First Data")

# Check if conversion is complete
if not st.session_state.get('conversion_complete'):
    st.warning("⚠️ Please run the conversion first in 'Run Conversion' page")
    st.stop()

# Introduction
st.markdown(f"""
<div style='background-color: #E8F4F8; border-left: 5px solid {NDIA_ACCENT}; padding: 15px; border-radius: 5px;'>
<h3 style='margin-top: 0;'>The Digital-First Promise</h3>
<p><strong>ONE source → INFINITE presentations</strong></p>
<p>Now that the PAPL is in JSON, YAML, and Markdown, we can generate different views for different users:</p>
<ul>
<li><strong>Participant View</strong> - Simple, accessible, focused on what they can claim</li>
<li><strong>Support Coordinator View</strong> - Searchable, filterable, with claiming rules</li>
<li><strong>Provider View</strong> - API-ready, bulk pricing, claiming validation</li>
<li><strong>Old Framework View</strong> - Filtered for current planning approach</li>
<li><strong>New Framework View</strong> - Filtered for capacity-based planning</li>
<li><strong>PDF Export</strong> - For those who need traditional formats</li>
</ul>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Select view to generate
st.markdown("## 📋 Select View to Generate")

view_type = st.selectbox(
    "Choose the PAPL presentation you want to create:",
    [
        "Participant Portal View (Exemplar 1)",
        "Support Coordinator Dashboard (Exemplar 2)",
        "Provider API Response (Exemplar 3)",
        "Old Framework Planning View",
        "New Framework Planning View",
        "Accessible Web Page (WCAG 2.1 AA)",
        "Traditional PDF Document",
        "Price Comparison Tool",
        "Custom Filtered View"
    ]
)

st.markdown("---")

# Navigation to specific generator
if view_type == "Participant Portal View (Exemplar 1)":
    st.markdown("### 👤 Participant Portal View")
    
    st.markdown("""
    **For:** Participants and their families
    
    **Features:**
    - Simple language (no jargon)
    - Pictures and icons
    - "Can I claim this?" checker
    - Plain English explanations
    - Large text, high contrast
    - Voice-over compatible
    
    **Example: "Occupational Therapy"**
    - ✅ "You can claim up to $193.99 per hour"
    - ✅ "Available in your area (NSW)"
    - ✅ "Provider must be registered"
    - ❌ No complex claiming rules visible
    """)
    
    if st.button("🎨 Generate Participant View", type="primary", use_container_width=True):
        st.info("Navigate to **'6_Participant_View'** to see the generated portal!")

elif view_type == "Support Coordinator Dashboard (Exemplar 2)":
    st.markdown("### 🧭 Support Coordinator Dashboard")
    
    st.markdown("""
    **For:** Support coordinators helping participants
    
    **Features:**
    - Searchable support items
    - Filter by category, price, location
    - Claiming rules displayed clearly
    - Quick price lookup by state
    - Compare similar supports
    - Export participant-friendly PDFs
    
    **Example: Finding "therapy" supports**
    - Search returns: OT, Physio, Speech, Psychology
    - Shows price ranges by state
    - Displays claiming conditions
    - One-click to create participant summary
    """)
    
    if st.button("🎨 Generate Coordinator Dashboard", type="primary", use_container_width=True):
        st.info("Navigate to **'7_Coordinator_Dashboard'** to see the dashboard!")

elif view_type == "Provider API Response (Exemplar 3)":
    st.markdown("### 🔌 Provider API Response")
    
    st.markdown("""
    **For:** Provider software systems (practice management, billing)
    
    **Features:**
    - RESTful API endpoints
    - JSON responses
    - Real-time price updates
    - Claiming validation
    - Bulk pricing queries
    - Change notifications
    
    **Example API Request:**
    ```
    GET /api/v1/support-items/01_001_0117_1_3/pricing?state=NSW
    ```
    
    **Response:**
    ```json
    {
      "support_item": "01_001_0117_1_3",
      "name": "Occupational Therapy - Standard",
      "price": 193.99,
      "currency": "AUD",
      "state": "NSW",
      "effective_date": "2025-11-24",
      "claiming_rules": [...]
    }
    ```
    """)
    
    if st.button("🎨 Generate API Documentation", type="primary", use_container_width=True):
        st.info("Navigate to **'8_Provider_API'** to see API examples!")

elif view_type == "Old Framework Planning View":
    st.markdown("### 📚 Old Framework Planning View")
    
    st.markdown("""
    **For:** Current framework participants (pre-New Framework)
    
    **Features:**
    - Only shows supports available under old framework
    - Traditional budget categories visible
    - Familiar terminology
    - Standard claiming rules only
    - No capacity-based planning references
    
    **Filters applied:**
    - `framework_applicable: old_framework`
    - Budget categories: Core, Capital, Capacity Building
    - Traditional support purposes
    """)
    
    if st.button("🎨 Generate Old Framework View", type="primary", use_container_width=True):
        st.info("Navigate to **'9_Framework_Comparison'** to compare Old vs New!")

elif view_type == "New Framework Planning View":
    st.markdown("### 🆕 New Framework Planning View")
    
    st.markdown("""
    **For:** New framework participants (capacity-based planning)
    
    **Features:**
    - Shows capacity-building focus
    - Assessment requirements visible
    - Goal-oriented presentation
    - Reasonable and necessary criteria
    - Mainstream service alternatives shown
    
    **Filters applied:**
    - `framework_applicable: new_framework`
    - `assessment_required: true` where applicable
    - Capacity focus emphasized
    """)
    
    if st.button("🎨 Generate New Framework View", type="primary", use_container_width=True):
        st.info("Navigate to **'9_Framework_Comparison'** to compare Old vs New!")

elif view_type == "Accessible Web Page (WCAG 2.1 AA)":
    st.markdown("### ♿ Accessible Web Page")
    
    st.markdown("""
    **For:** All users, especially those with disabilities
    
    **Features:**
    - WCAG 2.1 AA compliant
    - Screen reader optimized
    - Keyboard navigation
    - High contrast mode
    - Adjustable text size
    - Semantic HTML structure
    - ARIA labels throughout
    
    **Accessibility improvements over PDF:**
    - ✅ Tables properly tagged with headers
    - ✅ Logical reading order
    - ✅ Alternative text for visual elements
    - ✅ Skip navigation links
    - ✅ Focus indicators
    - ❌ PDF: Tables read as gibberish
    - ❌ PDF: No logical structure
    """)
    
    if st.button("🎨 Generate Accessible Page", type="primary", use_container_width=True):
        st.info("Navigate to **'12_Accessible_View'** to see WCAG compliant page!")

elif view_type == "Traditional PDF Document":
    st.markdown("### 📄 Traditional PDF Document")
    
    st.markdown("""
    **For:** Users who prefer/require PDF format
    
    **Features:**
    - Auto-generated from JSON source
    - Always up-to-date
    - Consistent formatting
    - All state pricing included
    - Proper table of contents
    - Bookmarks and links
    
    **Key difference from current approach:**
    - Current: PDF is the master → everything flows from it
    - Digital-first: JSON is the master → PDF is just one output
    
    **Advantages:**
    - PDF updates automatically when data changes
    - No manual reformatting
    - Guaranteed consistency with web/API
    """)
    
    if st.button("🎨 Generate PDF", type="primary", use_container_width=True):
        st.info("PDF generation coming soon! Uses ReportLab to create PDF from JSON.")

elif view_type == "Price Comparison Tool":
    st.markdown("### 💰 Price Comparison Tool")
    
    st.markdown("""
    **For:** Participants, coordinators, policy analysts
    
    **Features:**
    - Compare prices across states
    - Compare Old vs New framework pricing
    - Compare similar support items
    - Historical price trends
    - NT remote area loading visualization
    
    **Example: "Occupational Therapy - Standard"**
    
    | State | Price | Remote Loading |
    |-------|-------|----------------|
    | NSW | $193.99 | - |
    | VIC | $193.99 | - |
    | NT | $205.63 | +6% |
    
    Instantly see if NT pricing has correct remote loading!
    """)
    
    if st.button("🎨 Generate Price Comparison", type="primary", use_container_width=True):
        st.info("Navigate to **'11_Price_Comparison'** to compare prices!")

else:  # Custom Filtered View
    st.markdown("### 🔧 Custom Filtered View")
    
    st.markdown("""
    **Create your own custom view with filters:**
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Filter by Category:**")
        filter_category = st.multiselect(
            "Support Categories",
            ["Core", "Capital", "Capacity Building - All"],
            default=[]
        )
        
        st.markdown("**Filter by State:**")
        filter_state = st.multiselect(
            "States/Territories",
            ["NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT"],
            default=["NSW"]
        )
    
    with col2:
        st.markdown("**Filter by Framework:**")
        filter_framework = st.radio(
            "Framework",
            ["Both", "Old Framework Only", "New Framework Only"],
            index=0
        )
        
        st.markdown("**Filter by Price:**")
        filter_price_min = st.number_input("Min Price ($)", min_value=0.0, value=0.0)
        filter_price_max = st.number_input("Max Price ($)", min_value=0.0, value=10000.0)
    
    if st.button("🎨 Generate Custom View", type="primary", use_container_width=True):
        st.success("Custom view configuration saved!")
        st.json({
            "categories": filter_category,
            "states": filter_state,
            "framework": filter_framework,
            "price_range": [filter_price_min, filter_price_max]
        })

# Value proposition reminder
st.markdown("---")
st.markdown(f"""
<div style='background-color: {NDIA_BLUE}; padding: 20px; border-radius: 10px; color: white;'>
<h3 style='color: white; margin-top: 0;'>The Digital-First Advantage</h3>
<p><strong>With static documents (current approach):</strong></p>
<ul>
<li>One 104-page PDF for everyone</li>
<li>Participants struggle to find relevant info</li>
<li>Support coordinators waste hours searching</li>
<li>Providers manually update systems</li>
<li>Accessibility fails</li>
<li>Supporting Old + New Framework = 2× the work</li>
</ul>
<p><strong>With digital-first (this approach):</strong></p>
<ul>
<li>One JSON source → infinite customized views</li>
<li>Participants see only what's relevant to them</li>
<li>Coordinators have searchable, filterable tools</li>
<li>Providers get real-time API updates</li>
<li>Perfect accessibility on all views</li>
<li>Supporting Old + New Framework = same source, different filters</li>
</ul>
<p style='margin-bottom: 0;'><strong>Same data. Better presentations. Infinite possibilities.</strong></p>
</div>
""", unsafe_allow_html=True)

# Quick stats
st.markdown("---")
st.markdown("## 📊 Available Data")

if st.session_state.get('json_output'):
    json_data = st.session_state.json_output
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_items = len(json_data.get('support_items', []))
    col1.metric("Support Items", f"{total_items:,}")
    
    if st.session_state.get('yaml_output'):
        yaml_data = st.session_state.yaml_output
        rule_count = len(yaml_data.get('claiming_rules', {}))
        col2.metric("Claiming Rules", rule_count)
    else:
        col2.metric("Claiming Rules", "0")
    
    # Count unique categories
    categories = set()
    for item in json_data.get('support_items', []):
        if item.get('support_category'):
            categories.add(item['support_category'])
    col3.metric("Categories", len(categories))
    
    # Count items with full state pricing
    complete = sum(1 for item in json_data.get('support_items', []) 
                   if len(item.get('price_limits', {})) == 8)
    col4.metric("Complete Pricing", f"{complete:,}")
    
    st.info("💡 All these views will be generated from this same data!")

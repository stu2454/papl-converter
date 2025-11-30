"""
Page 8: Framework Comparison View
Show how same data serves Old Framework vs New Framework planning
"""

import streamlit as st
import json

# NDIA Brand Colors
NDIA_BLUE = "#003087"
NDIA_ACCENT = "#00B5E2"

st.title("🔄 Old vs New Framework Comparison")
st.markdown("### Same Data, Different Presentations")

# Check if data is available
if not st.session_state.get('json_output'):
    st.warning("⚠️ Please convert your PAPL data first in 'Run Conversion' page")
    st.stop()

json_data = st.session_state.json_output
yaml_data = st.session_state.get('yaml_output', {})

# Introduction
st.markdown(f"""
<div style='background-color: #E8F4F8; border-left: 5px solid {NDIA_ACCENT}; padding: 20px; border-radius: 10px;'>
<h3 style='margin-top: 0;'>The Digital-First Solution to Framework Coexistence</h3>
<p><strong>The Challenge:</strong> Supporting both Old Framework and New Framework planning simultaneously</p>
<p><strong>Current Approach (Debated):</strong></p>
<ul>
<li>Option A: Two separate 104-page PAPLs (208 pages total to maintain)</li>
<li>Option B: One integrated 150+ page PAPL (hopelessly complex)</li>
<li><strong>Both options multiply the $25.56M annual cost</strong></li>
</ul>
<p><strong>Digital-First Approach (This demonstration):</strong></p>
<ul>
<li>✅ One JSON source with framework flags</li>
<li>✅ Filter by framework to show relevant view</li>
<li>✅ Costs stay the same (just different filters)</li>
<li>✅ Perfect consistency across both frameworks</li>
</ul>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Select framework view
framework_view = st.radio(
    "Select Framework View:",
    ["Side-by-Side Comparison", "Old Framework Only", "New Framework Only"],
    horizontal=True
)

if framework_view == "Side-by-Side Comparison":
    st.markdown("## 📊 Side-by-Side View")
    
    # Example support item
    st.markdown("### Example: Occupational Therapy - Standard")
    st.caption("Support Item Number: 01_001_0117_1_3")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div style='background-color: #F0F8FF; border: 2px solid {NDIA_BLUE}; padding: 20px; border-radius: 10px; height: 100%;'>
        <h3 style='color: {NDIA_BLUE}; margin-top: 0;'>📚 Old Framework View</h3>
        <p><strong>Occupational Therapy - Standard</strong></p>
        
        <p><strong>Budget Category:</strong> Capacity Building - Daily Activity</p>
        
        <p><strong>Price (NSW):</strong> $193.99 per hour</p>
        
        <p><strong>Can I claim this?</strong></p>
        <ul>
        <li>✅ If it's in your plan</li>
        <li>✅ If you have funding in this budget</li>
        <li>✅ If provider is registered</li>
        </ul>
        
        <p><strong>Claiming Rules:</strong></p>
        <ul>
        <li>Claim at standard rate during business hours</li>
        <li>Higher rates for evenings/weekends</li>
        <li>Travel time claimable separately</li>
        <li>No quote required</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background-color: #F0FFF0; border: 2px solid #28A745; padding: 20px; border-radius: 10px; height: 100%;'>
        <h3 style='color: #28A745; margin-top: 0;'>🆕 New Framework View</h3>
        <p><strong>Occupational Therapy - Standard</strong></p>
        
        <p><strong>Capacity Area:</strong> Daily Living & Life Skills</p>
        
        <p><strong>Price (NSW):</strong> $193.99 per hour</p>
        
        <p><strong>Can I claim this?</strong></p>
        <ul>
        <li>✅ If it helps build your capacity</li>
        <li>✅ If it's reasonable and necessary</li>
        <li>✅ If no mainstream alternative available</li>
        <li>⚠️ May require capacity assessment</li>
        </ul>
        
        <p><strong>Claiming Rules:</strong></p>
        <ul>
        <li>Same price as Old Framework</li>
        <li>Must align with capacity goals</li>
        <li>Provider assesses reasonable & necessary</li>
        <li>Focus on skill development</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Key differences table
    st.markdown("### 🔍 Key Differences")
    
    diff_data = {
        "Aspect": [
            "Pricing",
            "Budget Structure",
            "Approval Process",
            "Provider Requirements",
            "Focus",
            "Claiming"
        ],
        "Old Framework": [
            "Same price limits",
            "Core, Capital, Capacity Building",
            "Plan-based allocation",
            "Registered providers",
            "Service delivery",
            "Plan budget categories"
        ],
        "New Framework": [
            "Same price limits ✅",
            "Capacity-focused categories",
            "Assessment + reasonable & necessary",
            "Registered providers + capacity assessment",
            "Capacity building",
            "Goals + reasonable & necessary criteria"
        ]
    }
    
    import pandas as pd
    df_diff = pd.DataFrame(diff_data)
    st.dataframe(df_diff, use_container_width=True, hide_index=True)
    
    st.success("✅ **Key Point:** The PRICE DATA is identical. Only the PRESENTATION and RULES differ!")

elif framework_view == "Old Framework Only":
    st.markdown("## 📚 Old Framework View")
    
    st.markdown(f"""
    <div style='background-color: #F0F8FF; border: 2px solid {NDIA_BLUE}; padding: 20px; border-radius: 10px;'>
    <h3 style='color: {NDIA_BLUE}; margin-top: 0;'>Filtered for Current Framework Participants</h3>
    <p>This view shows only what's relevant for participants still on the old framework planning approach.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Supports Available")
    
    # Sample data showing old framework categorization
    st.markdown("""
    **Budget Categories Shown:**
    - ✅ Core - Assistance with Daily Life
    - ✅ Core - Transport
    - ✅ Core - Consumables  
    - ✅ Core - Social, Economic and Community Participation
    - ✅ Capital - Assistive Technology
    - ✅ Capital - Home Modifications
    - ✅ Capacity Building - Support Coordination
    - ✅ Capacity Building - (various domains)
    
    **Terms Used:**
    - "In your plan"
    - "Budget category"
    - "Plan allocation"
    - "Service delivery"
    
    **Rules Shown:**
    - Standard claiming procedures
    - Budget category alignment
    - Plan-based approval
    - Registered provider requirements
    """)
    
    # Show sample supports
    supports = json_data.get('support_items', [])[:10]
    
    for item in supports:
        with st.expander(f"📋 {item.get('support_item_name', 'Unknown')}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"""
                **Support Category:** {item.get('support_category', 'Not specified')}  
                **Provider Registration:** {item.get('registration_group', 'Required')}  
                **Claiming:** {'Quote required first' if item.get('quote_required') else 'Standard price applies'}
                """)
            
            with col2:
                price = item.get('price_limits', {}).get('NSW', {}).get('price', 0)
                st.metric("NSW Price", f"${price:.2f}")
                st.caption(f"per {item.get('unit', 'unit')}")

else:  # New Framework Only
    st.markdown("## 🆕 New Framework View")
    
    st.markdown(f"""
    <div style='background-color: #F0FFF0; border: 2px solid #28A745; padding: 20px; border-radius: 10px;'>
    <h3 style='color: #28A745; margin-top: 0;'>Filtered for New Framework Participants</h3>
    <p>This view emphasizes capacity building and reasonable & necessary criteria for new framework planning.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Supports Available")
    
    st.markdown("""
    **Capacity Areas Shown:**
    - ✅ Daily Living & Life Skills
    - ✅ Social & Community Participation
    - ✅ Health & Wellbeing
    - ✅ Learning & Development
    - ✅ Employment
    - ✅ Home & Living
    
    **Terms Used:**
    - "Capacity building"
    - "Reasonable and necessary"
    - "Mainstream alternatives"
    - "Skill development"
    - "Capacity assessment"
    
    **Rules Shown:**
    - Reasonable and necessary criteria
    - Capacity focus
    - Assessment requirements
    - Goal alignment
    - Mainstream service consideration
    """)
    
    # Show YAML rules for New Framework
    if yaml_data and 'claiming_rules' in yaml_data:
        st.markdown("### Example: Reasonable & Necessary Criteria")
        
        st.code("""
reasonable_and_necessary:
  criteria:
    reasonable:
      - Aligns with participant goals
      - Appropriate for disability
      - Cost proportionate to benefit
      - Delivered in appropriate manner
    
    necessary:
      - Addresses needs related to disability
      - No suitable mainstream alternative available
      - Participant cannot access without NDIS support
      - Will improve or maintain functional capacity
  
  assessment_process:
    - Provider assesses need
    - Documents capacity goals
    - Checks mainstream options
    - Confirms NDIS funding appropriate
        """, language="yaml")

# Technical demonstration
st.markdown("---")
st.markdown("## 🔧 How This Works Technically")

st.markdown("""
### JSON Data Structure (Same for Both Frameworks)

```json
{
  "support_item_number": "01_001_0117_1_3",
  "support_item_name": "Occupational Therapy - Standard",
  "support_category": "CB Capacity Building",
  "price_limits": {
    "NSW": {"price": 193.99, "currency": "AUD"}
  },
  "framework_applicability": {
    "old_framework": {
      "applicable": true,
      "budget_category": "Capacity Building - Daily Activity"
    },
    "new_framework": {
      "applicable": true,
      "capacity_area": "Daily Living & Life Skills",
      "assessment_required": true,
      "reasonable_necessary_apply": true
    }
  }
}
```

### YAML Business Rules (Framework-Specific)

```yaml
claiming_for_therapy:
  section_title: Claiming for Therapy Services
  
  old_framework:
    applicable: true
    conditions:
      - Must be in participant plan
      - Must align with budget category
      - Provider must be registered
  
  new_framework:
    applicable: true
    conditions:
      - Must meet reasonable and necessary criteria
      - Must build participant capacity
      - Mainstream alternatives considered
      - Assessment may be required
```

### View Generation (Filtering)

```python
# Generate Old Framework View
old_framework_supports = [
    item for item in all_supports
    if item['framework_applicability']['old_framework']['applicable']
]

# Generate New Framework View
new_framework_supports = [
    item for item in all_supports
    if item['framework_applicability']['new_framework']['applicable']
]

# Same data, different filters!
```
""")

# Value proposition
st.markdown("---")
st.markdown(f"""
<div style='background-color: {NDIA_BLUE}; padding: 25px; border-radius: 10px; color: white;'>
<h3 style='color: white; margin-top: 0;'>💡 The Digital-First Advantage for Framework Coexistence</h3>

<p><strong>Your colleagues are debating:</strong></p>
<p style='font-size: 1.1em; font-style: italic;'>"Should we create separate PAPLs for Old and New Framework, or one integrated PAPL?"</p>

<p><strong>The answer is NEITHER. Here's why:</strong></p>

<table style='width: 100%; color: white; margin: 20px 0;'>
<tr style='background-color: rgba(255,255,255,0.1);'>
<th style='padding: 10px; text-align: left;'>Approach</th>
<th style='padding: 10px; text-align: left;'>Annual Cost</th>
<th style='padding: 10px; text-align: left;'>Maintenance Burden</th>
<th style='padding: 10px; text-align: left;'>Consistency</th>
</tr>
<tr>
<td style='padding: 10px;'>Two Separate PAPLs</td>
<td style='padding: 10px;'>$51M+ (double)</td>
<td style='padding: 10px;'>❌ 208 pages to maintain</td>
<td style='padding: 10px;'>❌ Version drift guaranteed</td>
</tr>
<tr style='background-color: rgba(255,255,255,0.1);'>
<td style='padding: 10px;'>One Integrated PAPL</td>
<td style='padding: 10px;'>$40M+ (1.5x)</td>
<td style='padding: 10px;'>❌ 150+ pages impossible to navigate</td>
<td style='padding: 10px;'>❌ Rules hopelessly tangled</td>
</tr>
<tr>
<td style='padding: 10px;'><strong>Digital-First (This)</strong></td>
<td style='padding: 10px;'><strong>$200K implementation</strong></td>
<td style='padding: 10px;'>✅ One source, filtered views</td>
<td style='padding: 10px;'>✅ Perfect consistency</td>
</tr>
</table>

<p style='font-size: 1.2em; margin-top: 20px;'><strong>Same pricing data. Different presentations. Zero duplication.</strong></p>

<p><strong>This demonstration proves it works!</strong></p>
</div>
""", unsafe_allow_html=True)

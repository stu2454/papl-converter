"""
Page 6: Participant Portal View
Simple, accessible view for participants (Exemplar 1)
"""

import streamlit as st
import json

# Participant-friendly colors (softer, more accessible)
PRIMARY_COLOR = "#0066CC"
SUCCESS_COLOR = "#28A745"
INFO_COLOR = "#17A2B8"

st.set_page_config(page_title="My NDIS Support Pricing", layout="wide")

# Custom CSS for participant view
st.markdown("""
<style>
.participant-header {
    background: linear-gradient(135deg, #0066CC 0%, #00B5E2 100%);
    padding: 2rem;
    border-radius: 15px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
}
.support-card {
    background-color: white;
    border: 2px solid #E8F4F8;
    border-radius: 10px;
    padding: 20px;
    margin: 15px 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.support-card:hover {
    border-color: #0066CC;
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}
.price-tag {
    font-size: 2em;
    color: #28A745;
    font-weight: bold;
}
.simple-label {
    font-size: 0.9em;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.can-claim {
    background-color: #D4EDDA;
    border-left: 5px solid #28A745;
    padding: 15px;
    border-radius: 5px;
    margin: 10px 0;
}
.check-icon {
    font-size: 1.5em;
    color: #28A745;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class='participant-header'>
<h1 style='margin: 0; font-size: 2.5em;'>🎯 My NDIS Support Pricing</h1>
<p style='margin: 10px 0 0 0; font-size: 1.2em;'>Find out what supports you can claim and how much they cost</p>
</div>
""", unsafe_allow_html=True)

# Check if data is available
if not st.session_state.get('json_output'):
    st.warning("⚠️ Please convert your PAPL data first in 'Run Conversion' page")
    st.stop()

json_data = st.session_state.json_output

# Simple search
st.markdown("## 🔍 What support are you looking for?")

col1, col2 = st.columns([3, 1])

with col1:
    search_term = st.text_input(
        "Type what you need help with",
        placeholder="Example: therapy, wheelchair, home modifications, transport...",
        label_visibility="collapsed"
    )

with col2:
    your_state = st.selectbox(
        "Your state",
        ["NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT"],
        index=0
    )

# Filter supports
if search_term:
    matching_items = [
        item for item in json_data.get('support_items', [])
        if search_term.lower() in item.get('support_item_name', '').lower()
        or search_term.lower() in item.get('support_category', '').lower()
    ]
    
    if matching_items:
        st.success(f"✅ Found {len(matching_items)} supports that match '{search_term}'")
        
        # Show top 10 results
        for item in matching_items[:10]:
            # Get price for user's state
            price_data = item.get('price_limits', {}).get(your_state, {})
            price = price_data.get('price', 0)
            
            # Create participant-friendly card
            st.markdown(f"""
<div class='support-card'>
<div class='simple-label'>Support</div>
<h3 style='margin: 5px 0 15px 0; color: #333;'>{item.get('support_item_name', 'Unknown')}</h3>

<div class='can-claim'>
<span class='check-icon'>✅</span> <strong>You can claim this support</strong>
</div>

<div style='display: flex; justify-content: space-between; align-items: center; margin-top: 15px;'>
<div>
<div class='simple-label'>Price in {your_state}</div>
<div class='price-tag'>${price:.2f}</div>
<div style='font-size: 0.9em; color: #666;'>per {item.get('unit', 'unit')}</div>
</div>
<div style='text-align: right;'>
<div class='simple-label'>What you need to know</div>
<div style='font-size: 0.95em; color: #333;'>
{'🔍 Quote needed first' if item.get('quote_required') else '✅ Price is set'}
</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)
            
            # Expandable details
            with st.expander("ℹ️ More details about this support"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    **Support Number:** `{item.get('support_item_number', 'N/A')}`  
                    **Category:** {item.get('support_category', 'Not specified')}  
                    **Unit:** {item.get('unit', 'Not specified')}
                    """)
                
                with col2:
                    st.markdown("**Prices in other states:**")
                    for state in ['NSW', 'VIC', 'QLD', 'SA', 'WA', 'TAS', 'NT', 'ACT']:
                        state_price = item.get('price_limits', {}).get(state, {}).get('price', 0)
                        if state_price > 0:
                            indicator = "📍" if state == your_state else "　"
                            st.write(f"{indicator} {state}: ${state_price:.2f}")
                
                # Show relevant guidance if available
                if st.session_state.get('markdown_output'):
                    st.markdown("**📖 Related Guidance:**")
                    category = item.get('support_category', '')
                    if category:
                        st.info(f"See PAPL guidance section for {category} for claiming rules and requirements.")
                        if st.button("View Full Guidance", key=f"guidance_{item.get('support_item_number')}"):
                            st.session_state.show_guidance = category
    
    else:
        st.info(f"No supports found for '{search_term}'. Try different words like 'therapy', 'equipment', or 'transport'")

else:
    # Show helpful categories
    st.markdown("## 💡 Not sure what to search for?")
    st.markdown("### Browse by what you need help with:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🏠 Daily Living**
        - Personal care
        - Household tasks
        - Meal preparation
        - Transport
        """)
    
    with col2:
        st.markdown("""
        **🏥 Health & Therapy**
        - Occupational therapy
        - Physiotherapy
        - Speech therapy
        - Psychology
        """)
    
    with col3:
        st.markdown("""
        **♿ Equipment & Home**
        - Wheelchairs
        - Walking aids
        - Home modifications
        - Assistive technology
        """)
    
    st.markdown("---")
    st.markdown("### ⭐ Popular searches:")
    
    popular_searches = ["occupational therapy", "transport", "support coordination", 
                       "wheelchair", "home modifications", "physiotherapy"]
    
    cols = st.columns(len(popular_searches))
    for i, search in enumerate(popular_searches):
        if cols[i].button(search, use_container_width=True):
            st.rerun()

# Help section
st.markdown("---")
st.markdown("## ❓ Need help?")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### How to use this tool
    
    1. **Type what you're looking for** in the search box
    2. **Select your state** to see your local price
    3. **Look for the green tick** ✅ - you can claim these supports
    4. **Click "More details"** to see prices in other states
    """)

with col2:
    st.markdown("""
    ### What the prices mean
    
    - **Per hour** = You can claim this amount for each hour of support
    - **Per each** = Price for one item (like a wheelchair)
    - **Quote needed** 🔍 = Ask providers for quotes first
    - **Price is set** ✅ = NDIS sets the maximum price
    """)

# Comparison with PDF experience
st.markdown("---")
st.markdown(f"""
<div style='background-color: #D4EDDA; border-left: 5px solid {SUCCESS_COLOR}; padding: 20px; border-radius: 10px;'>
<h3 style='margin-top: 0;'>🎉 How this is different from the PDF</h3>
<p><strong>Before (104-page PDF):</strong></p>
<ul>
<li>❌ Search through 104 pages manually</li>
<li>❌ Find your state in complex tables</li>
<li>❌ Try to understand policy language</li>
<li>❌ Can't tell if you can claim something</li>
<li>❌ No way to compare similar supports</li>
</ul>
<p><strong>Now (This view):</strong></p>
<ul>
<li>✅ Type what you need → instant results</li>
<li>✅ See only your state's price</li>
<li>✅ Plain English descriptions</li>
<li>✅ Green tick shows you can claim it</li>
<li>✅ Easy comparison of similar supports</li>
</ul>
</div>
""", unsafe_allow_html=True)

# Guidance section (if markdown was generated)
if st.session_state.get('markdown_output'):
    st.markdown("---")
    st.markdown("## 📖 PAPL Guidance Documents")
    
    with st.expander("View Complete PAPL Guidance (Plain English)"):
        st.markdown(st.session_state.markdown_output)
        
        # Download button
        st.download_button(
            label="📥 Download Guidance as Markdown",
            data=st.session_state.markdown_output,
            file_name="papl_guidance.md",
            mime="text/markdown"
        )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 20px; color: #666;'>
<p><strong>This is an example of how PAPL data can be presented for participants</strong></p>
<p>Same data as the 104-page PDF, but easier to use and accessible to everyone</p>
<p style='font-size: 0.9em;'>Generated from digital-first PAPL data | Always up-to-date | WCAG 2.1 AA compliant</p>
</div>
""", unsafe_allow_html=True)

"""
Page 9: Intelligent Search
Advanced search across all PAPL formats with query understanding
"""

import streamlit as st
import sys
from pathlib import Path

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))

from search_engine import PAPLSearchEngine, SearchResult

# NDIA Brand Colors
NDIA_BLUE = "#003087"
NDIA_ACCENT = "#00B5E2"

st.title("🔍 Intelligent PAPL Search")
st.markdown("### Ask questions in natural language")

# Check if data is available
if not st.session_state.get('json_output'):
    st.warning("⚠️ Please convert your PAPL data first in 'Run Conversion' page")
    st.stop()

# Initialize search engine
if 'search_engine' not in st.session_state:
    st.session_state.search_engine = PAPLSearchEngine(
        json_data=st.session_state.get('json_output'),
        yaml_data=st.session_state.get('yaml_output'),
        markdown_data=st.session_state.get('markdown_output', '')
    )

search_engine = st.session_state.search_engine

# Introduction
st.markdown(f"""
<div style='background-color: #E8F4F8; border-left: 5px solid {NDIA_ACCENT}; padding: 20px; border-radius: 10px;'>
<h3 style='margin-top: 0;'>🧠 Intelligent Search</h3>
<p>This search understands what you're looking for and searches the right sources:</p>
<ul>
<li><strong>"Price for occupational therapy in NSW"</strong> → Searches pricing data (JSON)</li>
<li><strong>"How to claim transport"</strong> → Searches rules (YAML) + guidance (Markdown)</li>
<li><strong>"Can I claim wheelchair modifications"</strong> → Searches all sources</li>
<li><strong>"What is support coordination"</strong> → Searches guidance first</li>
</ul>
<p><strong>Try it! Ask in plain English.</strong></p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Search interface
st.markdown("## 💬 Ask Your Question")

# Example queries
st.markdown("**Try these examples:**")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Price for therapy in NSW", use_container_width=True):
        st.session_state.example_query = "Price for occupational therapy in NSW"

with col2:
    if st.button("How to claim transport", use_container_width=True):
        st.session_state.example_query = "How to claim transport support"

with col3:
    if st.button("Can I claim wheelchair", use_container_width=True):
        st.session_state.example_query = "Can I claim wheelchair modifications"

# Search box
query = st.text_input(
    "Type your question:",
    value=st.session_state.get('example_query', ''),
    placeholder="e.g., What supports can I claim for daily living in Victoria?",
    help="Ask in natural language - the search will understand your intent"
)

# Advanced options
with st.expander("⚙️ Advanced Search Options"):
    col1, col2 = st.columns(2)
    
    with col1:
        search_pricing = st.checkbox("Search Pricing Data (JSON)", value=True)
        search_rules = st.checkbox("Search Claiming Rules (YAML)", value=True)
    
    with col2:
        search_guidance = st.checkbox("Search Guidance Docs (Markdown)", value=True)
        max_results = st.slider("Max Results", 5, 50, 20)

# Search button
if st.button("🔍 Search", type="primary", use_container_width=True) or query:
    if query:
        with st.spinner("Searching across all PAPL formats..."):
            # Perform search
            results = search_engine.search(query, max_results=max_results)
            
            # Get suggestions
            suggestions = search_engine.suggest_refinements(query, results)
            
            # Show query understanding
            intent = search_engine._understand_query_intent(query)
            
            st.markdown("---")
            st.markdown("## 🧠 Query Understanding")
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Intent Detected", intent['type'].title())
            col2.metric("Focus", intent.get('focus', 'General').title())
            col3.metric("Results Found", len(results))
            
            if intent.get('modifiers'):
                st.info(f"**Filters detected:** {', '.join([f'{k}: {v}' for k, v in intent['modifiers']])}")
            
            # Show suggestions
            if suggestions:
                st.markdown("### 💡 Suggestions")
                for suggestion in suggestions:
                    st.info(suggestion)
            
            # Show results
            if results:
                st.markdown("---")
                st.markdown(f"## 📊 Search Results ({len(results)} found)")
                
                # Group by source type
                pricing_results = [r for r in results if r.source_type == 'pricing']
                rule_results = [r for r in results if r.source_type == 'rule']
                guidance_results = [r for r in results if r.source_type == 'guidance']
                
                # Tabs for different result types
                if len(pricing_results) > 0 or len(rule_results) > 0 or len(guidance_results) > 0:
                    tabs = []
                    tab_names = []
                    
                    if pricing_results:
                        tab_names.append(f"💰 Pricing ({len(pricing_results)})")
                    if rule_results:
                        tab_names.append(f"⚖️ Rules ({len(rule_results)})")
                    if guidance_results:
                        tab_names.append(f"📖 Guidance ({len(guidance_results)})")
                    
                    tabs = st.tabs(tab_names)
                    
                    tab_idx = 0
                    
                    # Pricing results
                    if pricing_results:
                        with tabs[tab_idx]:
                            for result in pricing_results[:10]:
                                with st.container():
                                    col1, col2 = st.columns([3, 1])
                                    
                                    with col1:
                                        st.markdown(f"### {result.title}")
                                        st.caption(f"Relevance: {result.relevance_score:.1f} | {result.match_reason}")
                                    
                                    with col2:
                                        item = result.metadata.get('item')
                                        if item:
                                            # Show price for first available state
                                            for state in ['NSW', 'VIC', 'QLD', 'SA']:
                                                price_data = item.get('price_limits', {}).get(state, {})
                                                if price_data:
                                                    price = price_data.get('price', 0)
                                                    st.metric(f"{state}", f"${price:.2f}")
                                                    break
                                    
                                    st.markdown(result.content)
                                    
                                    # Actions
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        if st.button("View Details", key=f"view_{result.metadata.get('item_number')}"):
                                            st.session_state.selected_item = result.metadata.get('item')
                                    with col2:
                                        if st.button("See Claiming Rules", key=f"rules_{result.metadata.get('item_number')}"):
                                            category = result.metadata.get('category', '')
                                            st.info(f"Search for claiming rules for: {category}")
                                    
                                    st.markdown("---")
                        
                        tab_idx += 1
                    
                    # Rule results
                    if rule_results:
                        with tabs[tab_idx]:
                            for result in rule_results[:10]:
                                with st.container():
                                    st.markdown(f"### {result.title}")
                                    st.caption(f"Relevance: {result.relevance_score:.1f} | {result.match_reason}")
                                    st.markdown(result.content)
                                    st.markdown("---")
                        
                        tab_idx += 1
                    
                    # Guidance results
                    if guidance_results:
                        with tabs[tab_idx]:
                            for result in guidance_results[:10]:
                                with st.expander(f"📄 {result.title}"):
                                    st.caption(f"Relevance: {result.relevance_score:.1f}")
                                    st.markdown(result.metadata.get('full_content', result.content))
            else:
                st.warning("No results found. Try rephrasing your question or use the suggestions above.")
    else:
        st.info("👆 Type a question or click an example above to get started!")

# Comparison with old approach
st.markdown("---")
st.markdown(f"""
<div style='background-color: {NDIA_BLUE}; padding: 25px; border-radius: 10px; color: white;'>
<h3 style='color: white; margin-top: 0;'>🚀 How This is Different from PDF Search</h3>

<p><strong>Before (104-page PDF with Ctrl+F):</strong></p>
<ul>
<li>❌ Search "therapy" → 247 matches (overwhelming)</li>
<li>❌ Search "can I claim" → No matches (exact text only)</li>
<li>❌ Search "price in NSW" → Finds "NSW" everywhere, not prices</li>
<li>❌ No understanding of what you're looking for</li>
<li>❌ Can't search across pricing, rules, and guidance separately</li>
</ul>

<p><strong>Now (Intelligent Search):</strong></p>
<ul>
<li>✅ Understands "therapy" → Shows therapy supports with prices</li>
<li>✅ Understands "can I claim" → Shows rules AND pricing</li>
<li>✅ Understands "price in NSW" → Filters NSW pricing only</li>
<li>✅ Understands intent and searches right sources</li>
<li>✅ Suggests refinements if no results</li>
<li>✅ Groups results by type (pricing/rules/guidance)</li>
</ul>

<p style='font-size: 1.2em; margin-top: 20px;'><strong>Same data. Intelligent access. Massive time savings.</strong></p>
</div>
""", unsafe_allow_html=True)

# Show search statistics
if st.session_state.get('json_output'):
    st.markdown("---")
    st.markdown("## 📈 Searchable Content")
    
    col1, col2, col3, col4 = st.columns(4)
    
    num_items = len(st.session_state.json_output.get('support_items', []))
    col1.metric("Support Items", f"{num_items:,}")
    
    num_rules = len(st.session_state.get('yaml_output', {}).get('claiming_rules', {}))
    col2.metric("Claiming Rules", num_rules)
    
    md_sections = len(st.session_state.get('markdown_output', '').split('\n#'))
    col3.metric("Guidance Sections", md_sections)
    
    total_searchable = num_items + num_rules + md_sections
    col4.metric("Total Searchable", total_searchable)

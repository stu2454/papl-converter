"""
Page 10: AI Assistant (RAG Demonstration)
Conversational AI assistant powered by RAG
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))

try:
    from papl_assistant import BedrockRAGAssistant
    BEDROCK_AVAILABLE = True
except ImportError as e:
    BEDROCK_AVAILABLE = False
    IMPORT_ERROR = str(e)

# NDIA Brand Colors
NDIA_BLUE = "#003087"
NDIA_ACCENT = "#00B5E2"

st.title("🤖 AI PAPL Assistant")
st.markdown("### Ask questions in plain English - Get AI-powered answers")

# TEMPORARY DEBUG - Add to sidebar
with st.sidebar:
    with st.expander("🐛 Debug: AWS Environment", expanded=True):
        st.write("**AWS_REGION:**", os.getenv('AWS_REGION', '❌ NOT SET'))
        access_key = os.getenv('AWS_ACCESS_KEY_ID', '')
        if access_key:
            st.write("**AWS_ACCESS_KEY_ID:**", access_key[:10] + "..." + access_key[-4:])
        else:
            st.write("**AWS_ACCESS_KEY_ID:**", '❌ NOT SET')
        secret_key = os.getenv('AWS_SECRET_ACCESS_KEY', '')
        if secret_key:
            st.write("**AWS_SECRET_ACCESS_KEY:**", f'✅ SET ({len(secret_key)} chars)')
        else:
            st.write("**AWS_SECRET_ACCESS_KEY:**", '❌ NOT SET')
        st.write("**BEDROCK_EMBEDDING_MODEL:**", os.getenv('BEDROCK_EMBEDDING_MODEL', '❌ NOT SET'))
        st.write("**BEDROCK_LLM_MODEL:**", os.getenv('BEDROCK_LLM_MODEL', '❌ NOT SET'))

# Check if data is available
if not st.session_state.get('json_output'):
    st.warning("⚠️ Please convert your PAPL data first in 'Run Conversion' page")
    st.stop()

# Check Bedrock availability
if not BEDROCK_AVAILABLE:
    st.error(f"""
    ❌ AWS Bedrock SDK not available
    
    **Error:** {IMPORT_ERROR}
    
    **To use the AI Assistant, install required packages:**
    ```bash
    pip install boto3 numpy
    ```
    """)
    st.stop()

# AWS Configuration
st.markdown("## 🔐 AWS Bedrock Configuration")

with st.expander("⚙️ Configure AWS Credentials", expanded=not st.session_state.get('bedrock_configured')):
    st.markdown("""
    **AWS Bedrock requires authentication.** Choose the most secure method:
    
    ### 🔐 Option 1: AWS CLI (Recommended for Development)
    ```bash
    aws configure
    AWS Access Key ID: YOUR_KEY
    AWS Secret Access Key: YOUR_SECRET
    Default region: ap-southeast-2
    ```
    Credentials stored securely in `~/.aws/credentials`
    
    ### 📝 Option 2: Environment Variables (.env file)
    Create a `.env` file in the app directory:
    ```bash
    AWS_REGION=ap-southeast-2
    BEDROCK_EMBEDDING_MODEL=amazon.titan-embed-text-v1
    BEDROCK_LLM_MODEL=anthropic.claude-3-sonnet-20240229-v1:0
    
    # Optional: Only if not using AWS CLI
    # AWS_ACCESS_KEY_ID=your-key
    # AWS_SECRET_ACCESS_KEY=your-secret
    ```
    **⚠️ Never commit .env to git!** (Already in .gitignore)
    
    ### 🚀 Option 3: IAM Role (Best for Production)
    For EC2/ECS deployment:
    - Create IAM role with Bedrock permissions
    - Attach to instance/task
    - No credentials needed in code!
    
    **Required AWS Permissions:**
    - `bedrock:InvokeModel` - To call Claude
    - `bedrock:InvokeModelWithResponseStream` - For streaming (optional)
    """)
    
    st.markdown("---")
    st.markdown("#### Override Configuration (Optional)")
    st.info("💡 Leave blank to use .env file or AWS CLI config")
    
    col1, col2 = st.columns(2)
    
    with col1:
        aws_region = st.selectbox(
            "AWS Region",
            ["", "ap-southeast-2", "us-east-1", "us-west-2", "eu-west-1"],
            index=0,
            help="Leave empty to use AWS_REGION from .env or AWS CLI config"
        )
    
    with col2:
        llm_model = st.selectbox(
            "Claude Model",
            [
                "",
                "anthropic.claude-3-sonnet-20240229-v1:0",
                "anthropic.claude-3-haiku-20240307-v1:0",
                "anthropic.claude-instant-v1"
            ],
            index=0,
            help="Leave empty to use BEDROCK_LLM_MODEL from .env"
        )
    
    if st.button("✓ Save Configuration", type="primary"):
        # Only save non-empty values (empty means use .env or AWS config)
        if aws_region:
            st.session_state.aws_region = aws_region
        if llm_model:
            st.session_state.llm_model = llm_model
        
        st.session_state.bedrock_configured = True
        st.success("✓ Configuration saved! Will use .env file or AWS CLI config for any unset values.")
        st.rerun()

# Initialize assistant
if 'papl_assistant' not in st.session_state and st.session_state.get('bedrock_configured'):
    with st.spinner("🚀 Initializing AWS Bedrock RAG Assistant... (This may take 30-60 seconds)"):
        try:
            # Prepare optional configuration (None means use env vars)
            init_config = {
                'json_data': st.session_state.get('json_output'),
                'yaml_data': st.session_state.get('yaml_output'),
                'markdown_data': st.session_state.get('markdown_output', '')
            }
            
            # Only add region/model if explicitly set in session state
            if st.session_state.get('aws_region'):
                init_config['aws_region'] = st.session_state.aws_region
            if st.session_state.get('llm_model'):
                init_config['llm_model'] = st.session_state.llm_model
            
            st.session_state.papl_assistant = BedrockRAGAssistant(**init_config)
            st.success("✓ AWS Bedrock RAG Assistant initialized!")
        except Exception as e:
            st.error(f"""
            ❌ Failed to initialize AWS Bedrock
            
            **Error:** {str(e)}
            
            **Common issues:**
            - AWS credentials not configured (run `aws configure`)
            - Bedrock not enabled in your AWS account
            - Model access not requested in Bedrock console
            - Incorrect region
            - Check .env file has correct AWS_REGION
            
            **To fix:**
            1. Configure AWS CLI: `aws configure`
            2. Enable Bedrock in AWS Console (Sydney region)
            3. Request model access for Claude 3 and Titan Embeddings
            4. Create .env file from .env.example
            """)
            st.stop()

if not st.session_state.get('papl_assistant'):
    st.info("👆 Please configure AWS credentials above to use the AI Assistant")
    st.stop()

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

assistant = st.session_state.papl_assistant

# Introduction
st.markdown(f"""
<div style='background-color: #E8F4F8; border-left: 5px solid {NDIA_ACCENT}; padding: 20px; border-radius: 10px;'>
<h3 style='margin-top: 0;'>🧠 RAG-Powered AI Assistant</h3>
<p><strong>This is next-generation PAPL access using:</strong></p>
<ul>
<li><strong>Retrieval:</strong> Finds relevant sections from JSON/YAML/Markdown</li>
<li><strong>Augmented:</strong> Adds context to your question</li>
<li><strong>Generation:</strong> AI generates natural language answers</li>
</ul>
<p><strong>Ask anything!</strong> The AI will:</p>
<ul>
<li>✅ Search all PAPL formats (JSON, YAML, Markdown)</li>
<li>✅ Find relevant pricing, rules, and guidance</li>
<li>✅ Generate a clear, accurate answer</li>
<li>✅ Cite its sources</li>
<li>✅ Explain in plain language</li>
</ul>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Model information
st.markdown("## ⚙️ Current Configuration")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("AWS Region", st.session_state.get('aws_region', 'Not configured'))

with col2:
    model_name = st.session_state.get('llm_model', 'Not configured')
    if 'sonnet' in model_name.lower():
        model_display = "Claude 3 Sonnet"
    elif 'haiku' in model_name.lower():
        model_display = "Claude 3 Haiku"
    else:
        model_display = "Claude Instant"
    st.metric("Model", model_display)

with col3:
    num_docs = len(st.session_state.papl_assistant.documents) if st.session_state.get('papl_assistant') else 0
    st.metric("Documents Indexed", f"{num_docs:,}")

# Retrieval settings
retrieval_docs = st.slider(
    "Documents to Retrieve",
    min_value=3,
    max_value=10,
    value=5,
    help="How many relevant document chunks to send to Claude"
)

st.markdown("---")

# Example questions
st.markdown("## 💬 Ask Your Question")

st.markdown("**Try these examples:**")
col1, col2 = st.columns(2)

with col1:
    if st.button("What's the price for occupational therapy in NSW?", use_container_width=True):
        st.session_state.demo_query = "What's the price for occupational therapy in NSW?"
    
    if st.button("How do I claim transport support?", use_container_width=True):
        st.session_state.demo_query = "How do I claim transport support?"

with col2:
    if st.button("Can I claim home modifications?", use_container_width=True):
        st.session_state.demo_query = "Can I claim home modifications? What do I need?"
    
    if st.button("What's the difference between old and new framework?", use_container_width=True):
        st.session_state.demo_query = "What's the difference between old and new framework planning?"

# Chat interface
query = st.text_input(
    "Your question:",
    value=st.session_state.get('demo_query', ''),
    placeholder="e.g., What supports can I claim for daily living? How much is support coordination?",
    help="Ask any question about NDIS pricing, claiming, or supports"
)

# Ask button
if st.button("🤖 Ask AI Assistant", type="primary", use_container_width=True) or query:
    if query and st.session_state.get('papl_assistant'):
        with st.spinner("🧠 AI is thinking... (Retrieving documents + Calling Claude on Bedrock)"):
            try:
                # Get AI response from Bedrock
                result = st.session_state.papl_assistant.ask(
                    query, 
                    top_k=retrieval_docs,
                    max_tokens=2000
                )
                
                # Add to chat history
                st.session_state.chat_history.append({
                    'query': query,
                    'result': result
                })
                
                # Clear demo query
                if 'demo_query' in st.session_state:
                    del st.session_state.demo_query
                    
            except Exception as e:
                st.error(f"""
                ❌ Error calling AWS Bedrock
                
                **Error:** {str(e)}
                
                **This might be because:**
                - AWS credentials expired
                - Bedrock quota exceeded  
                - Model not available in region
                - Network connectivity issue
                """)
    elif not st.session_state.get('papl_assistant'):
        st.warning("Please configure AWS credentials above first")

# Display chat history (most recent first)
if st.session_state.chat_history:
    st.markdown("---")
    st.markdown("## 💬 Conversation")
    
    for i, chat in enumerate(reversed(st.session_state.chat_history)):
        with st.container():
            # User question
            st.markdown(f"""
            <div style='background-color: #F0F8FF; padding: 15px; border-radius: 10px; margin-bottom: 10px;'>
            <strong>You asked:</strong><br>
            {chat['query']}
            </div>
            """, unsafe_allow_html=True)
            
            # AI answer
            st.markdown(f"""
            <div style='background-color: #F0FFF0; padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
            <strong>🤖 AI Assistant:</strong><br>
            {chat['result']['answer']}
            </div>
            """, unsafe_allow_html=True)
            
            # Show sources used
            with st.expander("📚 Sources Used"):
                sources = chat['result'].get('sources', [])
                
                st.markdown(f"**Retrieved {len(sources)} relevant documents:**")
                
                for j, doc in enumerate(sources, 1):
                    st.markdown(f"""
                    **Document {j} ({doc.source_type.upper()})**
                    ```
                    {doc.content[:300]}...
                    ```
                    """)
            
            # Show RAG prompt (for technical users)
            with st.expander("🔍 Technical Details (RAG Prompt)"):
                st.markdown("**This is the prompt sent to the AI with retrieved context:**")
                st.text_area(
                    "Full Prompt",
                    value=chat['result'].get('prompt', ''),
                    height=400,
                    key=f"prompt_{i}"
                )
            
            st.markdown("---")

# Clear history button
if st.session_state.chat_history:
    if st.button("🗑️ Clear Conversation History"):
        st.session_state.chat_history = []
        st.rerun()

# RAG Architecture explanation
st.markdown("---")
st.markdown("## 🏗️ How RAG Works")

st.markdown("""
### The Process

```
1. USER QUESTION
   "What's the price for occupational therapy in NSW?"
         ↓
2. RETRIEVAL (Search PAPL Documents)
   → Search JSON pricing data
   → Search YAML claiming rules
   → Search Markdown guidance
   → Find 5 most relevant chunks
         ↓
3. AUGMENTATION (Add Context to Prompt)
   → Build prompt with:
      - System instructions
      - Retrieved documents as context
      - User question
      - Response guidelines
         ↓
4. GENERATION (AI Creates Answer)
   → Send prompt to LLM (Claude/GPT-4)
   → AI reads context
   → AI generates natural language answer
   → AI cites sources used
         ↓
5. USER RECEIVES ANSWER
   "Occupational Therapy - Standard is priced at $193.99 
    per hour in NSW. According to Document 1..."
```
""")

# Benefits comparison
st.markdown("---")
st.markdown(f"""
<div style='background-color: {NDIA_BLUE}; padding: 25px; border-radius: 10px; color: white;'>
<h3 style='color: white; margin-top: 0;'>🚀 RAG vs. Traditional Approaches</h3>

<table style='width: 100%; color: white;'>
<tr style='background-color: rgba(255,255,255,0.1);'>
<th style='padding: 10px; text-align: left;'>Approach</th>
<th style='padding: 10px; text-align: left;'>User Experience</th>
<th style='padding: 10px; text-align: left;'>Accuracy</th>
</tr>
<tr>
<td style='padding: 10px;'><strong>PDF Search (Ctrl+F)</strong></td>
<td style='padding: 10px;'>❌ Find keywords manually<br>❌ Read entire sections<br>❌ Interpret yourself</td>
<td style='padding: 10px;'>⚠️ Depends on user skill</td>
</tr>
<tr style='background-color: rgba(255,255,255,0.1);'>
<td style='padding: 10px;'><strong>Keyword Search</strong></td>
<td style='padding: 10px;'>⚠️ Get list of results<br>⚠️ Click through each<br>⚠️ Piece together answer</td>
<td style='padding: 10px;'>⚠️ Better but still manual</td>
</tr>
<tr>
<td style='padding: 10px;'><strong>Intelligent Search</strong></td>
<td style='padding: 10px;'>✅ Get ranked results<br>⚠️ Still need to read<br>⚠️ Combine information</td>
<td style='padding: 10px;'>✅ Good relevance</td>
</tr>
<tr style='background-color: rgba(255,255,255,0.1);'>
<td style='padding: 10px;'><strong>RAG AI Assistant</strong></td>
<td style='padding: 10px;'>✅ Ask in plain English<br>✅ Get direct answer<br>✅ With sources cited</td>
<td style='padding: 10px;'>✅ High accuracy<br>✅ Verifiable</td>
</tr>
</table>

<p style='font-size: 1.2em; margin-top: 20px;'><strong>RAG = Best of both worlds: AI intelligence + Document accuracy</strong></p>
</div>
""", unsafe_allow_html=True)

# Production considerations
st.markdown("---")
st.markdown("## 🏢 Production Implementation")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### Recommended Stack for NDIA
    
    **LLM: Anthropic Claude API**
    - Australian company (data sovereignty)
    - Excellent at following instructions
    - Strong reasoning capabilities
    - Citations and source tracking
    - Cost: ~$3-15 per 1M tokens
    
    **Alternative: Azure OpenAI**
    - Australian data centers available
    - Government compliance ready
    - NDIA likely has Azure account
    - Same GPT-4 models as OpenAI
    """)

with col2:
    st.markdown("""
    ### Infrastructure Needed
    
    **Vector Database:**
    - Azure Cognitive Search (recommended)
    - Or ChromaDB (open source)
    - Or Pinecone (managed service)
    
    **Embeddings:**
    - Azure OpenAI embeddings
    - Or sentence-transformers (local)
    
    **Cost Estimate:**
    - LLM API: ~$500-2000/month
    - Vector DB: ~$200-500/month
    - Total: ~$700-2500/month
    
    **vs. Current manual costs:** $25.56M/year
    **ROI:** 10,000x+
    """)

# Costs and benefits
st.markdown("---")
st.markdown("## 💰 Cost-Benefit Analysis")

metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)

metrics_col1.metric(
    "Monthly API Cost",
    "$700-2500",
    help="LLM API + Vector DB + Embeddings"
)

metrics_col2.metric(
    "Annual Cost",
    "$8K-30K",
    help="Total infrastructure cost"
)

metrics_col3.metric(
    "vs. Current Cost",
    "$25.56M",
    delta="-99.9%",
    delta_color="normal",
    help="Annual hidden cost of manual approach"
)

metrics_col4.metric(
    "ROI",
    "850x - 3,000x",
    help="First year return on investment"
)

st.success("""
**The numbers speak for themselves:** Even with premium AI services, the cost is negligible 
compared to the $25.56M annual hidden cost of the current manual approach.
""")

# Next steps
st.markdown("---")
st.markdown("## 🎯 Next Steps to Production")

st.markdown("""
### Phase 1: Pilot (2-4 weeks)
1. ✅ Set up Azure OpenAI account (or Anthropic API)
2. ✅ Integrate embeddings and vector database
3. ✅ Test with actual PAPL documents
4. ✅ Pilot with 3 exemplar users
5. ✅ Measure accuracy and satisfaction

### Phase 2: MVP (2-3 months)
1. Deploy to production infrastructure
2. Add user authentication
3. Implement usage analytics
4. Create feedback loop
5. Monitor and improve prompts

### Phase 3: Scale (6 months)
1. Expand to all PAPL content
2. Add multi-user support
3. Integrate with myplace portal
4. Provider API access
5. Continuous learning from usage

### Phase 4: Enhancement (12 months)
1. Multi-turn conversations (chatbot)
2. Personalization by user type
3. Proactive suggestions
4. Predictive analytics
5. Integration with planning tools
""")

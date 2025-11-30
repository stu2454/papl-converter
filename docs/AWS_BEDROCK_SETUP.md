# AWS Bedrock RAG - Setup Guide

## 🎯 Real Production Implementation

This is a **real, working AWS Bedrock RAG implementation** - not a simulation!

### Components
- ✅ **AWS Bedrock** - Managed Claude 3 Sonnet/Haiku
- ✅ **Titan Embeddings** - Amazon's embedding model (1536 dimensions)
- ✅ **Semantic Search** - Cosine similarity on embedded documents
- ✅ **Production-ready** - Error handling, logging, monitoring

---

## 🔐 AWS Setup (One-Time)

### Step 1: Enable AWS Bedrock

1. **Log into AWS Console**
   - Go to: https://console.aws.amazon.com
   - Region: Select **ap-southeast-2** (Sydney) for Australian data sovereignty

2. **Navigate to Bedrock**
   - Search for "Bedrock" in services
   - Click "Amazon Bedrock"

3. **Enable Model Access**
   - Left sidebar → "Model access"
   - Click "Manage model access"
   - Enable:
     - ✅ **Anthropic - Claude 3 Sonnet**
     - ✅ **Anthropic - Claude 3 Haiku** (optional, cheaper)
     - ✅ **Amazon - Titan Embeddings G1 - Text**
   - Click "Request model access"
   - Wait 5-10 minutes for approval (usually instant)

### Step 2: Create IAM User/Role

**Option A: IAM User (for development)**

```bash
# 1. Create IAM user in AWS Console
# 2. Attach policy:
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": [
                "arn:aws:bedrock:ap-southeast-2::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0",
                "arn:aws:bedrock:ap-southeast-2::foundation-model/amazon.titan-embed-text-v1"
            ]
        }
    ]
}

# 3. Create access keys
# 4. Save access key ID and secret access key
```

**Option B: IAM Role (for EC2/ECS deployment)**

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel"
            ],
            "Resource": "*"
        }
    ]
}
```

Attach to EC2 instance or ECS task.

### Step 3: Configure AWS Credentials

**Local Development:**

```bash
# Install AWS CLI
pip install awscli

# Configure credentials
aws configure

# Enter:
# AWS Access Key ID: YOUR_KEY
# AWS Secret Access Key: YOUR_SECRET
# Default region: ap-southeast-2
# Default output format: json

# Test it works
aws bedrock list-foundation-models --region ap-southeast-2
```

**Environment Variables:**

```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="ap-southeast-2"
```

**For Production (EC2/ECS):**
- Attach IAM role to instance
- No credentials needed in code

---

## 📦 Install Dependencies

```bash
# Install Python packages
pip install boto3 numpy

# Or using requirements.txt
pip install -r requirements.txt
```

---

## 🚀 Using the Bedrock RAG Assistant

### In the Streamlit App

1. **Upload & Convert PAPL**
   - Go to "Upload Inputs"
   - Upload PAPL Word doc + Support Catalogue Excel
   - Go to "Run Conversion"
   - Convert to JSON/YAML/Markdown

2. **Configure AWS**
   - Go to "AI Assistant" page
   - Expand "Configure AWS Credentials"
   - Select region: **ap-southeast-2** (Sydney)
   - Select model: **Claude 3 Sonnet** (recommended)
   - Click "Save Configuration"

3. **Initialize Assistant**
   - Wait 30-60 seconds while it:
     - Builds document corpus (622+ chunks)
     - Creates embeddings via Bedrock Titan
     - Initializes vector search

4. **Ask Questions!**
   - "What's the price for occupational therapy in NSW?"
   - "How do I claim transport support?"
   - "Can I claim home modifications?"

### Programmatically

```python
from papl_assistant import BedrockRAGAssistant

# Initialize
assistant = BedrockRAGAssistant(
    json_data=your_json_data,
    yaml_data=your_yaml_data,
    markdown_data=your_markdown_data,
    aws_region='ap-southeast-2',
    embedding_model='amazon.titan-embed-text-v1',
    llm_model='anthropic.claude-3-sonnet-20240229-v1:0'
)

# Ask a question
result = assistant.ask("What's the price for OT in NSW?")
print(result['answer'])

# See sources
for doc in result['sources']:
    print(f"Source: {doc.source_type} - {doc.chunk_id}")

# Simple chat interface
answer = assistant.chat("How do I claim wheelchairs?")
print(answer)
```

---

## 💰 Costs

### Per Query Breakdown

**Embedding Costs (Titan Embeddings):**
- Input: ~500 tokens per query (to embed query)
- Cost: $0.0001 per 1K tokens
- **Per query:** ~$0.00005 (negligible)

**LLM Costs (Claude 3 Sonnet):**
- Input: ~2000 tokens (context from 5 documents)
- Output: ~500 tokens (answer)
- Input cost: $3 per 1M tokens = $0.006
- Output cost: $15 per 1M tokens = $0.0075
- **Per query:** ~$0.014 (1.4 cents)

**Total per query:** ~$0.014

### Monthly Estimates

| Queries/Month | Embedding Cost | LLM Cost | Total/Month |
|---------------|----------------|----------|-------------|
| 1,000 | $0.05 | $14 | **$14** |
| 10,000 | $0.50 | $140 | **$140** |
| 50,000 | $2.50 | $700 | **$702** |
| 100,000 | $5.00 | $1,400 | **$1,405** |

**vs. Current manual cost:** $25.56M/year

**ROI even at 100K queries/month:** ~1,500x

### Cost Optimization

**Use Claude 3 Haiku for simpler queries:**
- 5x cheaper than Sonnet
- Still very capable
- Good for FAQ-style questions

```python
assistant = BedrockRAGAssistant(
    llm_model='anthropic.claude-3-haiku-20240307-v1:0'
)
```

**Implement caching:**
```python
# Cache common queries
if query in cache:
    return cache[query]
else:
    result = assistant.ask(query)
    cache[query] = result
    return result
```

---

## 🔍 How It Works

### Architecture

```
User Question
     ↓
[1] EMBED QUERY (Bedrock Titan)
     ↓
[2] SEMANTIC SEARCH (Cosine Similarity)
     → Find top 5 most similar document chunks
     ↓
[3] BUILD PROMPT
     → System instructions
     → Retrieved context (5 documents)
     → User question
     ↓
[4] CALL CLAUDE (Bedrock)
     → Claude reads context
     → Claude generates answer
     → Claude cites sources
     ↓
Answer with Citations
```

### Document Chunking

**622 Support Items → 622 pricing documents**
```
Each support item becomes one searchable chunk with:
- Item name and number
- All state pricing
- Category information
- Quote requirements
```

**14 Claiming Rules → 14 rule documents**
```
Each YAML claiming rule becomes one chunk with:
- Rule name
- Conditions
- Requirements
```

**Guidance Sections → N guidance documents**
```
Markdown split by ## headers into sections
```

**Total:** ~650-700 searchable document chunks

### Semantic Search

**Query:** "wheelchair"

**Traditional keyword search:**
- Finds: Documents with exact word "wheelchair"
- Misses: "mobility aid", "powered chair"

**Semantic search with embeddings:**
```
"wheelchair" → [0.23, -0.15, 0.87, ..., 0.42]  # 1536-dim vector

Find similar vectors:
- "wheelchair" → similarity: 0.95
- "mobility aid" → similarity: 0.82
- "powered chair" → similarity: 0.78
- "walking frame" → similarity: 0.65

Returns top 5 most semantically similar documents
```

---

## 📊 Monitoring

### CloudWatch Metrics

Bedrock automatically logs:
- Number of invocations
- Token usage
- Latency
- Errors

**View in AWS Console:**
1. CloudWatch → Metrics
2. Bedrock namespace
3. Filter by model ID

### Custom Logging

```python
import logging

logging.basicConfig(level=logging.INFO)

# Logs included in assistant:
# ✓ Bedrock initialized
# ✓ Documents embedded
# ✓ Query processing steps
# ✓ Retrieval results
# ✓ Response received
```

### Cost Tracking

**Enable AWS Cost Explorer:**
1. Billing Dashboard → Cost Explorer
2. Filter by service: Bedrock
3. Group by: Model ID
4. View daily/monthly costs

---

## 🛡️ Security Best Practices

### 1. Credentials

**DO:**
- ✅ Use IAM roles for EC2/ECS
- ✅ Rotate access keys regularly
- ✅ Use AWS Secrets Manager for keys
- ✅ Least privilege permissions

**DON'T:**
- ❌ Commit credentials to git
- ❌ Share access keys
- ❌ Use root account credentials
- ❌ Hardcode keys in code

### 2. Data Privacy

**DO:**
- ✅ Use Sydney region (data sovereignty)
- ✅ Enable CloudTrail logging
- ✅ Encrypt data at rest
- ✅ Use VPC endpoints for Bedrock

**DON'T:**
- ❌ Log sensitive participant data
- ❌ Store PII in embeddings
- ❌ Use public regions for sensitive data

### 3. Rate Limiting

```python
# Implement rate limiting
from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=100, period=60)  # 100 calls per minute
def ask_with_limit(query):
    return assistant.ask(query)
```

---

## 🐛 Troubleshooting

### Issue: "ResourceNotFoundException"

**Problem:** Model not found

**Solution:**
1. Check model ID is correct
2. Verify model access granted in Bedrock console
3. Wait 5-10 mins after requesting access
4. Check you're in the right region

### Issue: "AccessDeniedException"

**Problem:** No permission to invoke model

**Solution:**
1. Check IAM policy includes `bedrock:InvokeModel`
2. Verify resource ARN is correct
3. Check AWS credentials are configured
4. Try: `aws bedrock list-foundation-models`

### Issue: "ThrottlingException"

**Problem:** Too many requests

**Solution:**
1. Implement rate limiting
2. Add exponential backoff
3. Request quota increase in AWS Console
4. Use Haiku for high-volume queries

### Issue: Slow initialization

**Problem:** Takes 60+ seconds to start

**Reason:** Creating 650+ embeddings via Bedrock API

**Solutions:**
1. **Cache embeddings** (save to file, load on startup)
2. **Pre-compute** embeddings offline
3. **Use fewer documents** for testing
4. **Batch embedding requests** (if supported)

**Example caching:**
```python
import pickle

# Save embeddings
with open('embeddings.pkl', 'wb') as f:
    pickle.dump(assistant.documents, f)

# Load embeddings  
with open('embeddings.pkl', 'rb') as f:
    assistant.documents = pickle.load(f)
```

---

## 🚀 Production Deployment

### EC2 Deployment

```bash
# 1. Launch EC2 instance (Sydney)
# 2. Attach IAM role with Bedrock permissions
# 3. Install dependencies
sudo yum install python3 pip
pip3 install -r requirements.txt

# 4. Run application
streamlit run app.py --server.port 8502
```

### ECS/Fargate Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8502
CMD ["streamlit", "run", "app.py", "--server.port=8502"]
```

**Task definition:**
- Assign IAM role with Bedrock permissions
- Environment variables: AWS_DEFAULT_REGION=ap-southeast-2
- Memory: 2GB (for embeddings)
- CPU: 1 vCPU

### Lambda (for API)

**Limitations:**
- 15 min timeout (may not be enough for initialization)
- Cold start issues with embeddings

**Better:** Use API Gateway → ECS/Fargate

---

## 📈 Next Steps

### Immediate
1. ✅ Test with AWS credentials
2. ✅ Try example queries
3. ✅ Verify costs in billing dashboard
4. ✅ Check CloudWatch logs

### Short-term
1. Implement embedding caching
2. Add monitoring dashboard
3. Set up CloudWatch alarms
4. Create usage analytics

### Long-term
1. Multi-turn conversations
2. User feedback loop
3. Prompt optimization
4. A/B testing different models

---

## ✅ Success Checklist

**AWS Configuration:**
- [ ] Bedrock enabled in ap-southeast-2
- [ ] Claude 3 Sonnet access granted
- [ ] Titan Embeddings access granted
- [ ] IAM user/role created
- [ ] Permissions configured
- [ ] AWS CLI working
- [ ] Credentials configured

**Application:**
- [ ] boto3 and numpy installed
- [ ] PAPL data converted
- [ ] Bedrock assistant initialized
- [ ] Can ask questions and get answers
- [ ] Sources are cited correctly
- [ ] Answers are accurate

**Monitoring:**
- [ ] CloudWatch metrics visible
- [ ] Cost tracking enabled
- [ ] Logs being captured
- [ ] Usage dashboard created

**You're ready to use production AWS Bedrock RAG!** 🎉

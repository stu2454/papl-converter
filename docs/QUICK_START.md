# Quick Start Guide - Secure AWS Bedrock Setup

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Python 3.9+
- AWS account with Bedrock enabled
- Git (optional)

---

## Step 1: Install Dependencies

```bash
cd papl_converter
pip install -r requirements.txt
```

**Installs:**
- streamlit (web app)
- boto3 (AWS SDK)
- numpy (vector math)
- python-dotenv (environment variables)
- Other dependencies

---

## Step 2: Configure AWS Credentials (Choose ONE Method)

### 🔐 Method A: AWS CLI (Recommended)

**Most secure for development - credentials stored in `~/.aws/credentials`**

```bash
# Install AWS CLI (if not already installed)
# macOS: brew install awscli
# Ubuntu: sudo apt install awscli
# Windows: Download from aws.amazon.com/cli

# Configure credentials
aws configure

# Enter your credentials:
AWS Access Key ID: YOUR_KEY_HERE
AWS Secret Access Key: YOUR_SECRET_HERE
Default region name: ap-southeast-2
Default output format: json

# Test it works
aws bedrock list-foundation-models --region ap-southeast-2
```

**✅ No need to touch .env file!** Boto3 will automatically use these credentials.

### 📝 Method B: .env File

**For custom configuration or CI/CD**

```bash
# Copy example file
cp .env.example .env

# Edit .env file
nano .env  # or use your favorite editor
```

**In .env:**
```bash
# AWS Configuration
AWS_REGION=ap-southeast-2

# Model Configuration
BEDROCK_EMBEDDING_MODEL=amazon.titan-embed-text-v1
BEDROCK_LLM_MODEL=anthropic.claude-3-sonnet-20240229-v1:0

# Only add these if NOT using AWS CLI:
# AWS_ACCESS_KEY_ID=your-key
# AWS_SECRET_ACCESS_KEY=your-secret
```

**⚠️ Security Warning:**
- `.env` is in `.gitignore` - it will NOT be committed to git
- **NEVER** remove `.env` from `.gitignore`
- **NEVER** commit AWS credentials to git

### 🚀 Method C: IAM Role (Production)

**Most secure for EC2/ECS deployment**

No credentials needed! AWS automatically provides them via instance metadata.

Just ensure your EC2 instance or ECS task has an IAM role with:
```json
{
  "Effect": "Allow",
  "Action": ["bedrock:InvokeModel"],
  "Resource": "*"
}
```

---

## Step 3: Enable Bedrock Model Access

**One-time setup in AWS Console:**

1. Go to: https://console.aws.amazon.com/bedrock
2. Select region: **ap-southeast-2** (Sydney)
3. Left sidebar → **Model access**
4. Click **Manage model access**
5. Enable:
   - ✅ Anthropic - Claude 3 Sonnet
   - ✅ Anthropic - Claude 3 Haiku (optional)
   - ✅ Amazon - Titan Embeddings G1 - Text
6. Click **Request model access**
7. Wait ~5-10 minutes (usually instant)

**Verify access:**
```bash
aws bedrock list-foundation-models --region ap-southeast-2 | grep claude
```

---

## Step 4: Run the Application

```bash
streamlit run app.py
```

**Or specify port:**
```bash
streamlit run app.py --server.port 8502
```

**Using Docker:**
```bash
docker-compose up --build
```

**Open browser:**
- http://localhost:8501 (or 8502 if using Docker)

---

## Step 5: Convert PAPL & Ask Questions

1. **Upload files** (Page 1)
   - Upload PAPL Word document
   - Upload Support Catalogue Excel

2. **Run conversion** (Page 3)
   - Convert to JSON/YAML/Markdown

3. **Go to AI Assistant** (Page 10)
   - Configure AWS (if needed)
   - Click "Save Configuration"
   - Wait 30-60 seconds for initialization
   - Ask questions!

**Example questions:**
- "What's the price for occupational therapy in NSW?"
- "How do I claim transport support?"
- "Can I claim home modifications?"

---

## ⚠️ Troubleshooting

### "ResourceNotFoundException: Could not find model"

**Problem:** Model access not granted

**Solution:**
1. Check Bedrock console → Model access
2. Ensure Claude 3 Sonnet is enabled
3. Wait 5-10 minutes after requesting access
4. Verify you're in ap-southeast-2 region

### "AccessDeniedException: User is not authorized"

**Problem:** AWS credentials missing or insufficient permissions

**Solution:**
1. Run `aws configure` to set up credentials
2. Verify credentials work: `aws sts get-caller-identity`
3. Check IAM policy includes `bedrock:InvokeModel`
4. Verify correct region in .env or AWS config

### "NoCredentialsError: Unable to locate credentials"

**Problem:** No AWS credentials found

**Solution:**
1. **Option A:** Run `aws configure` (recommended)
2. **Option B:** Add credentials to .env file:
   ```bash
   AWS_ACCESS_KEY_ID=your-key
   AWS_SECRET_ACCESS_KEY=your-secret
   ```
3. **Option C:** Ensure IAM role attached (if on EC2/ECS)

### "ThrottlingException: Rate exceeded"

**Problem:** Too many requests

**Solution:**
1. Implement rate limiting in code
2. Request quota increase in AWS Console
3. Use Haiku model (higher quota, cheaper)

### App initializes slowly (60+ seconds)

**Expected behavior:** Creating embeddings for 650+ documents takes time

**To speed up:**
1. Cache embeddings (save to file, load on startup)
2. Pre-compute embeddings offline
3. Use fewer documents for testing

---

## 🔒 Security Checklist

Before deploying or sharing:

- [ ] `.env` file is in `.gitignore` ✅ (already done)
- [ ] No credentials hardcoded in Python files
- [ ] Using AWS CLI or IAM roles (not .env credentials)
- [ ] Shared `.env.example` (not `.env`)
- [ ] Team members create their own `.env` files
- [ ] MFA enabled on AWS account
- [ ] Least privilege IAM policy
- [ ] CloudTrail logging enabled
- [ ] Reviewed SECURITY_BEST_PRACTICES.md

---

## 📁 Project Structure

```
papl_converter/
├── app.py                          # Main Streamlit app
├── requirements.txt                # Python dependencies
├── .env.example                    # Example config (SAFE to commit)
├── .env                            # Your config (NEVER commit)
├── .gitignore                      # Protects .env
├── Dockerfile                      # Docker deployment
├── docker-compose.yml              # Docker orchestration
├── lib/
│   ├── converter.py                # PAPL → JSON/YAML/Markdown
│   ├── search_engine.py            # Intelligent search
│   └── papl_assistant.py           # AWS Bedrock RAG
├── pages/
│   ├── 1_Upload_Inputs.py
│   ├── 3_Run_Conversion.py
│   ├── 9_Intelligent_Search.py
│   └── 10_AI_Assistant.py          # Bedrock integration
└── docs/
    ├── AWS_BEDROCK_SETUP.md        # Detailed AWS guide
    ├── SECURITY_BEST_PRACTICES.md  # Security guide
    └── ...
```

---

## 📚 Documentation

- **AWS Setup:** See `AWS_BEDROCK_SETUP.md`
- **Security:** See `SECURITY_BEST_PRACTICES.md`
- **Docker:** See `DOCKER_GUIDE.md`
- **Deployment:** See `DEPLOYMENT_GUIDE.md`

---

## 💰 Cost Estimate

**Development (100 queries):** ~$1.40
**Production (10,000 queries/month):** ~$140/month

Compare to manual process: $25.56M/year

**ROI:** ~180,000x

---

## 🆘 Need Help?

**Common Issues:**
1. Credentials → Read `SECURITY_BEST_PRACTICES.md`
2. Model access → See `AWS_BEDROCK_SETUP.md` Step 1
3. Docker → See `DOCKER_GUIDE.md`

**Still stuck?**
1. Check CloudWatch logs in AWS Console
2. Run with debug logging: `streamlit run app.py --logger.level=debug`
3. Review error messages carefully
4. Ensure all prerequisites met

---

## ✅ Success Checklist

You're ready when:

- [ ] `pip install -r requirements.txt` completes
- [ ] AWS credentials configured (AWS CLI or .env)
- [ ] Bedrock model access granted in AWS Console
- [ ] `aws bedrock list-foundation-models` returns results
- [ ] Streamlit app starts without errors
- [ ] Can upload and convert PAPL
- [ ] AI Assistant initializes successfully
- [ ] Can ask questions and get answers
- [ ] .env file NOT in git (`git status` doesn't show it)

**🎉 You're ready to use AWS Bedrock RAG!**

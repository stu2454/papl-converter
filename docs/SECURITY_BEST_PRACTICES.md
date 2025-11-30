# Security Best Practices - AWS Bedrock & PAPL Converter

## 🔐 Critical Security Principles

### Never Hardcode Secrets!

**❌ NEVER DO THIS:**
```python
# BAD - Hardcoded credentials in code
aws_access_key = "AKIAIOSFODNN7EXAMPLE"
aws_secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

client = boto3.client(
    'bedrock-runtime',
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key
)
```

**✅ DO THIS INSTEAD:**
```python
# GOOD - Let boto3 use credential chain
client = boto3.client('bedrock-runtime')  # Automatically finds credentials
```

---

## 🔑 AWS Credential Management

### Credential Chain Priority (boto3)

When you don't explicitly pass credentials, boto3 searches in this order:

1. **Environment variables**
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_SESSION_TOKEN` (for temporary credentials)

2. **Shared credentials file**
   - `~/.aws/credentials` (created by `aws configure`)

3. **AWS config file**
   - `~/.aws/config`

4. **IAM role** (when running on AWS infrastructure)
   - EC2 instance profile
   - ECS task role
   - Lambda execution role

5. **Container credentials** (ECS)

6. **Instance metadata service** (EC2)

### Recommended Approaches by Environment

#### 🖥️ Local Development

**Use AWS CLI:**
```bash
aws configure
```

This creates `~/.aws/credentials`:
```ini
[default]
aws_access_key_id = YOUR_KEY
aws_secret_access_key = YOUR_SECRET
region = ap-southeast-2
```

**Advantages:**
- ✅ Credentials stored outside project
- ✅ Shared across all AWS tools
- ✅ Easy to rotate
- ✅ Won't accidentally commit to git

#### 🏢 Team Development

**Use .env file (with .gitignore):**

`.env`:
```bash
AWS_REGION=ap-southeast-2
BEDROCK_EMBEDDING_MODEL=amazon.titan-embed-text-v1
BEDROCK_LLM_MODEL=anthropic.claude-3-sonnet-20240229-v1:0

# Only if not using AWS CLI
# AWS_ACCESS_KEY_ID=your-key
# AWS_SECRET_ACCESS_KEY=your-secret
```

`.gitignore`:
```
.env
*.env
!.env.example
```

**Advantages:**
- ✅ Per-project configuration
- ✅ Easy to switch between environments
- ✅ Team members can have different credentials
- ✅ Protected by .gitignore

**Remember:**
- Share `.env.example` (without secrets)
- **NEVER** commit `.env` to git
- Each team member creates their own `.env`

#### 🚀 Production (EC2/ECS)

**Use IAM Roles:**

1. **Create IAM role** with Bedrock permissions:
```json
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
```

2. **Attach role to instance/task**
   - EC2: Attach instance profile
   - ECS: Attach task execution role

3. **No credentials needed in code or .env!**

**Advantages:**
- ✅ Most secure - no credentials in files
- ✅ Automatic credential rotation
- ✅ Fine-grained permissions per service
- ✅ Audit trail in CloudTrail

---

## 🔒 Environment Variable Security

### Development (.env file)

```bash
# .env - NEVER commit to git!

# AWS Configuration
AWS_REGION=ap-southeast-2

# Model Configuration  
BEDROCK_EMBEDDING_MODEL=amazon.titan-embed-text-v1
BEDROCK_LLM_MODEL=anthropic.claude-3-sonnet-20240229-v1:0

# Credentials (use AWS CLI instead when possible)
# AWS_ACCESS_KEY_ID=  # Leave empty to use AWS CLI
# AWS_SECRET_ACCESS_KEY=  # Leave empty to use AWS CLI
```

### Loading Environment Variables

**In Python:**
```python
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Access variables
region = os.getenv('AWS_REGION', 'ap-southeast-2')  # Default if not set
model = os.getenv('BEDROCK_LLM_MODEL', 'anthropic.claude-3-sonnet-20240229-v1:0')
```

**In Docker:**
```dockerfile
# docker-compose.yml
services:
  app:
    env_file:
      - .env  # Load from .env file
    environment:
      - AWS_REGION=ap-southeast-2  # Or set directly
```

---

## 🛡️ AWS IAM Best Practices

### Principle of Least Privilege

**Don't use AdministratorAccess!**

**❌ Too Permissive:**
```json
{
  "Effect": "Allow",
  "Action": "*",
  "Resource": "*"
}
```

**✅ Minimal Permissions:**
```json
{
  "Effect": "Allow",
  "Action": [
    "bedrock:InvokeModel"
  ],
  "Resource": [
    "arn:aws:bedrock:ap-southeast-2::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0"
  ]
}
```

### Separate Users for Different Purposes

**Don't use same credentials for everything:**

- **Developer 1:** Read-only Bedrock access
- **Developer 2:** Bedrock invoke + S3 read
- **Production App:** Bedrock invoke only (via IAM role)
- **Admin:** Full access (use MFA)

### Enable MFA

For IAM users with console access:
1. IAM → Users → Security credentials
2. Assign MFA device
3. Require MFA for sensitive operations

### Rotate Credentials Regularly

**For access keys:**
```bash
# Create new key
aws iam create-access-key --user-name your-username

# Update .env or ~/.aws/credentials with new key

# Test new key works
aws bedrock list-foundation-models

# Delete old key
aws iam delete-access-key --access-key-id OLD_KEY_ID --user-name your-username
```

**Rotation schedule:**
- Development: Every 90 days
- Production: Use IAM roles (auto-rotating)

---

## 📝 .gitignore Configuration

**Always include:**

```gitignore
# Environment files
.env
.env.local
.env.production
.env.*.local
*.env

# AWS credentials
.aws/
*.pem
*.key
credentials

# Secrets
secrets/
*.secret

# Keep example files
!.env.example
```

**Test your .gitignore:**
```bash
# Check what would be committed
git status

# If .env shows up, it's NOT in .gitignore!
# Fix immediately:
echo ".env" >> .gitignore
git add .gitignore
git commit -m "Add .env to gitignore"

# Remove from git history if already committed
git rm --cached .env
git commit -m "Remove .env from version control"
```

---

## 🔍 Secrets Scanning

### Pre-commit Hooks

Install git-secrets:
```bash
# macOS
brew install git-secrets

# Ubuntu
git clone https://github.com/awslabs/git-secrets
cd git-secrets
sudo make install

# Initialize for your repo
cd /path/to/papl_converter
git secrets --install
git secrets --register-aws
```

Now git will prevent commits with AWS keys!

### GitHub Advanced Security

If using GitHub:
1. Enable "Secret scanning" in repo settings
2. Enable "Push protection"
3. GitHub will block pushes with secrets

---

## 🚨 What If Credentials Are Exposed?

### Immediate Actions

**If you committed AWS credentials to git:**

1. **Immediately rotate credentials:**
   ```bash
   aws iam create-access-key --user-name your-username
   aws iam delete-access-key --access-key-id EXPOSED_KEY_ID --user-name your-username
   ```

2. **Check CloudTrail for unauthorized usage:**
   - AWS Console → CloudTrail
   - Look for suspicious API calls
   - Check if anyone used exposed credentials

3. **Remove from git history:**
   ```bash
   # Use BFG Repo-Cleaner
   java -jar bfg.jar --delete-files .env
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   
   # Force push (coordinate with team!)
   git push --force
   ```

4. **Notify security team** (if in organization)

5. **Review IAM policies:**
   - Remove any overly permissive policies
   - Enable CloudTrail logging
   - Set up CloudWatch alarms

**If you think credentials might be exposed:**

1. **Rotate immediately** (better safe than sorry)
2. **Review access logs**
3. **Update team on new credentials**

---

## 🔐 Production Security Checklist

### Before Deployment

- [ ] No credentials in code
- [ ] No credentials in git history
- [ ] .env in .gitignore
- [ ] Using IAM roles (not access keys)
- [ ] Least privilege IAM policies
- [ ] MFA enabled for all users
- [ ] CloudTrail logging enabled
- [ ] CloudWatch alarms for unusual activity
- [ ] Secrets in AWS Secrets Manager (if needed)
- [ ] VPC endpoints for Bedrock (if possible)
- [ ] Encryption at rest enabled
- [ ] Encryption in transit (HTTPS)
- [ ] Input validation for user queries
- [ ] Rate limiting implemented
- [ ] Audit logging enabled

### AWS Secrets Manager (Optional)

For even better security in production:

```python
import boto3
import json

def get_secret():
    client = boto3.client('secretsmanager', region_name='ap-southeast-2')
    response = client.get_secret_value(SecretId='papl-converter/bedrock')
    secret = json.loads(response['SecretString'])
    return secret

# Use in code
config = get_secret()
model = config['llm_model']
```

**Advantages:**
- ✅ Centralized secret management
- ✅ Automatic rotation
- ✅ Audit trail
- ✅ Fine-grained access control
- ✅ Encrypted at rest

---

## 📊 Security Monitoring

### CloudTrail

**Enable logging:**
1. CloudTrail → Create trail
2. Log all Bedrock API calls
3. Send to S3 bucket
4. Set up alarms for suspicious activity

**Monitor for:**
- Unusual number of API calls
- Calls from unexpected IP addresses
- Calls to unauthorized models
- Failed authentication attempts

### CloudWatch Alarms

**Create alarms for:**
```python
# Example: Alert if >1000 Bedrock calls in 5 minutes
aws cloudwatch put-metric-alarm \
  --alarm-name bedrock-high-usage \
  --metric-name InvokedModelCount \
  --namespace AWS/Bedrock \
  --statistic Sum \
  --period 300 \
  --threshold 1000 \
  --comparison-operator GreaterThanThreshold
```

### Cost Alerts

**Set billing alerts:**
1. Billing → Budgets
2. Create budget for Bedrock
3. Alert at 50%, 80%, 100% of budget

---

## 🎓 Security Training

**Team education:**
- Regular security training
- Code review for credential handling
- Incident response plan
- Regular security audits

**Resources:**
- [AWS Security Best Practices](https://aws.amazon.com/architecture/security-identity-compliance/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [AWS Well-Architected Framework - Security Pillar](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html)

---

## ✅ Quick Reference

### ✅ DO

- Use AWS CLI or IAM roles
- Store config in .env (never credentials)
- Add .env to .gitignore
- Use principle of least privilege
- Rotate credentials regularly
- Monitor CloudTrail logs
- Enable MFA
- Use HTTPS
- Validate all inputs
- Rate limit API calls

### ❌ DON'T

- Hardcode credentials in code
- Commit .env to git
- Share credentials between users
- Use root account credentials
- Give AdministratorAccess
- Log credentials
- Expose credentials in error messages
- Use same credentials for dev/prod
- Ignore security alerts
- Skip security reviews

---

**Remember: Security is everyone's responsibility!**

If you see credentials in code or git, speak up. Better to catch it before deployment than after a breach.

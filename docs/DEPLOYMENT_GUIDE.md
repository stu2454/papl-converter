# PAPL to Digital-First Converter - Deployment Guide

## Quick Start

### Option 1: Local Python Installation

```bash
# Extract the zip file
unzip papl_converter_app.zip
cd papl_converter

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py

# Open browser to http://localhost:8501
```

### Option 2: Docker Deployment

```bash
# Extract the zip file
unzip papl_converter_app.zip
cd papl_converter

# Build Docker image
docker build -t papl-converter .

# Run container
docker run -p 8501:8501 papl-converter

# Open browser to http://localhost:8501
```

### Option 3: Deploy to Render

```bash
# 1. Create GitHub repository
git init
git add .
git commit -m "Initial commit - PAPL Converter"
git remote add origin <your-repo-url>
git push -u origin main

# 2. Connect to Render
# - Go to render.com
# - Create new "Web Service"
# - Connect your GitHub repo
# - Use these settings:
#   - Build Command: pip install -r requirements.txt
#   - Start Command: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

---

## Package Contents

```
papl_converter/
├── app.py                      # Main application
├── requirements.txt            # Dependencies
├── README.md                   # Documentation
├── Dockerfile                  # Docker config
├── DEPLOYMENT_GUIDE.md         # This file
├── pages/                      # Application pages
│   ├── 1_Upload_Inputs.py
│   ├── 3_Run_Conversion.py
│   └── 4_View_Results.py
├── lib/                        # Core libraries
│   └── converter.py
└── outputs/                    # Generated files
```

---

## Usage Workflow

### Step 1: Upload Files

1. Launch the app
2. Navigate to **"📥 Upload Inputs"**
3. Upload your PAPL Word document (.docx)
4. Upload your Support Catalogue Excel (.xlsx)
5. Wait for analysis to complete

**Example files needed:**
- `NDIS Pricing Arrangements and Price Limits 2025-26 v1.1.docx`
- `NDIS-Support Catalogue-2025-26-v1.1.xlsx`

### Step 2: Run Conversion

1. Navigate to **"🔄 Run Conversion"**
2. Review conversion options:
   - ✅ Convert Support Catalogue to JSON
   - ✅ Convert Claiming Rules to YAML
   - ✅ Convert Guidance to Markdown
3. Enable validation options:
   - ✅ Validate State Pricing
   - ✅ Check NT Remote Loading
4. Click **"🚀 Start Conversion"**
5. Monitor progress bar
6. Review completion summary

### Step 3: View Results

1. Navigate to **"📊 View Results"**
2. Explore tabs:
   - **JSON Data** - Browse structured pricing
   - **YAML Rules** - Review business rules
   - **Markdown Guidance** - Read formatted guidance
   - **All Files** - Download everything

### Step 4: Analyze Validation

1. Check validation results in conversion summary
2. Review errors and warnings
3. Download validation report

### Step 5: Export Package

1. Navigate to **"📦 Export Package"**
2. Click **"Download ZIP Package"**
3. Extract files for use

---

## Expected Outputs

After conversion, you'll have:

### 1. support_catalogue.json
**Purpose:** Structured pricing data  
**Size:** ~500KB - 2MB depending on catalogue size  
**Contains:**
- All support items with pricing by state
- Metadata (categories, registration groups)
- Validation-ready structure

**Sample:**
```json
{
  "metadata": {
    "source": "NDIS Support Catalogue",
    "total_items": 622
  },
  "support_items": [
    {
      "support_item_number": "01_001_0117_1_3",
      "support_item_name": "Occupational Therapy - Standard",
      "price_limits": {
        "NSW": {"price": 193.99, "currency": "AUD"}
      }
    }
  ]
}
```

### 2. claiming_rules.yaml
**Purpose:** Business rules and conditions  
**Size:** ~50KB - 200KB  
**Contains:**
- 14+ claiming rule sections from PAPL
- Conditions extracted from text
- Framework applicability

**Sample:**
```yaml
claiming_rules:
  claiming_for_telehealth_services:
    section_title: Claiming for Telehealth Services
    conditions:
      - Provider must have appropriate technology
      - Participant must consent
    framework_specific:
      old_framework:
        applicable: true
```

### 3. papl_guidance.md
**Purpose:** Human-readable guidance  
**Size:** ~100KB - 500KB  
**Contains:**
- All PAPL sections formatted in Markdown
- Proper heading hierarchy
- Accessible format

### 4. validation_report.json
**Purpose:** Data quality analysis  
**Size:** ~10KB - 50KB  
**Contains:**
- Errors found (missing data, inconsistencies)
- Warnings (incomplete pricing, etc.)
- Recommendations

**Sample:**
```json
[
  {
    "type": "missing_state_pricing",
    "severity": "warning",
    "item": "01_002_0103_1_3",
    "missing_states": ["TAS"]
  },
  {
    "type": "pricing_inconsistency",
    "severity": "warning",
    "item": "01_005_0107_1_3",
    "message": "NT price should be ~6% higher than NSW"
  }
]
```

---

## Demonstration Scenarios

### Scenario 1: Internal Stakeholder Demo

**Purpose:** Show transformation to Branch Manager

**Steps:**
1. Upload actual PAPL 2025-26 files
2. Run full conversion
3. Show JSON output: "622 support items, validated, ready for API"
4. Show YAML rules: "14 claiming sections, now testable"
5. Show validation report: "Caught 15 data quality issues that PDFs can't detect"
6. **Key Message:** "This catches errors automatically that currently require manual review"

### Scenario 2: Pilot Participant Demo

**Purpose:** Show benefits to support coordinator

**Steps:**
1. Upload files
2. Run conversion
3. Navigate to View Results
4. Search for "Occupational Therapy"
5. Show JSON structure vs PDF lookup
6. **Key Message:** "Instant search vs 10 minutes finding page in PDF"

### Scenario 3: Technical Validation

**Purpose:** Prove concept to ICT team

**Steps:**
1. Upload files
2. Run conversion
3. Show validation report
4. Demonstrate NT remote loading check
5. Show API-ready JSON structure
6. **Key Message:** "Production-ready data structure with automated validation"

---

## Troubleshooting

### Issue: "Module not found" errors

**Solution:**
```bash
pip install --upgrade -r requirements.txt
```

### Issue: Streamlit won't start

**Solution:**
```bash
# Check Python version (need 3.9+)
python --version

# Reinstall streamlit
pip uninstall streamlit
pip install streamlit>=1.28.0

# Run with explicit path
python -m streamlit run app.py
```

### Issue: Upload fails

**Solution:**
- Ensure files are .docx and .xlsx format (not .doc or .xls)
- Check file isn't password protected
- Verify file size < 200MB

### Issue: Conversion fails

**Solution:**
- Check error message in app
- Verify Word document has tables and sections
- Ensure Excel has proper column headers
- Review validation report for specific issues

### Issue: Docker won't build

**Solution:**
```bash
# Clear Docker cache
docker system prune -a

# Rebuild with no cache
docker build --no-cache -t papl-converter .
```

---

## Performance Notes

### File Size Limits
- Word PAPL: Up to 50MB (typical: 500KB)
- Excel Catalogue: Up to 100MB (typical: 2-5MB)
- Processing time: 30 seconds - 2 minutes

### Memory Requirements
- Minimum: 2GB RAM
- Recommended: 4GB RAM
- Docker: Allocate 2GB to container

### Browser Compatibility
- Chrome (recommended)
- Firefox
- Safari
- Edge

---

## Integration Examples

### Use JSON Output in Python

```python
import json
import requests

# Load converted data
with open('support_catalogue.json') as f:
    catalogue = json.load(f)

# Find support item
def find_item(item_number):
    for item in catalogue['support_items']:
        if item['support_item_number'] == item_number:
            return item
    return None

# Get pricing for state
item = find_item('01_001_0117_1_3')
nsw_price = item['price_limits']['NSW']['price']
print(f"NSW Price: ${nsw_price}")
```

### Use YAML Rules in Application

```python
import yaml

# Load rules
with open('claiming_rules.yaml') as f:
    rules = yaml.safe_load(f)

# Check if rule applies
def can_claim_telehealth(framework='old'):
    rule = rules['claiming_rules']['claiming_for_telehealth_services']
    return rule['framework_specific'][f'{framework}_framework']['applicable']

print(can_claim_telehealth('new'))  # True
```

### Serve as API (Conceptual)

```python
from flask import Flask, jsonify
import json

app = Flask(__name__)

# Load data once
with open('support_catalogue.json') as f:
    catalogue = json.load(f)

@app.route('/api/v1/support-items/<item_number>')
def get_support_item(item_number):
    for item in catalogue['support_items']:
        if item['support_item_number'] == item_number:
            return jsonify(item)
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/v1/pricing/<state>/<item_number>')
def get_pricing(state, item_number):
    for item in catalogue['support_items']:
        if item['support_item_number'] == item_number:
            if state in item['price_limits']:
                return jsonify(item['price_limits'][state])
    return jsonify({'error': 'Not found'}), 404

if __name__ == '__main__':
    app.run(port=5000)
```

---

## Next Steps After Demo

### For Pilot
1. Select 3 specific PAPL sections
2. Convert with this tool
3. Build pilot-specific interfaces using JSON/YAML outputs
4. Measure time savings vs PDF

### For Production
1. Enhance conversion logic with AI/ML
2. Add comprehensive validation rules
3. Integrate with existing NDIA systems
4. Build provider API
5. Create automated deployment pipeline

### For Advocacy
1. Present conversion results to stakeholders
2. Show validation catching real errors
3. Demonstrate multi-framework capability
4. Quantify time/cost savings

---

## Support

### Documentation
- README.md - Full application documentation
- This file - Deployment and usage guide
- In-app help - Click ℹ️ icons for context

### Questions
- Check validation report for specific errors
- Review conversion logs in terminal
- Refer to PAPL analysis document

---

**Version:** 1.0  
**Date:** November 2025  
**Status:** Production-Ready Demonstration

**You're ready to demonstrate digital-first PAPL transformation!**

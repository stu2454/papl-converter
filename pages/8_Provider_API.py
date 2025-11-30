import streamlit as st
import json
import yaml
from pathlib import Path

st.set_page_config(
    page_title="Provider API - PAPL Converter",
    page_icon="🔌",
    layout="wide"
)

st.title("🔌 Provider API")
st.markdown("**REST API examples for third-party provider software integration**")

# Check if data is available
if not st.session_state.get('json_output'):
    st.warning("⚠️ Please convert your PAPL data first in 'Run Conversion' page")
    st.stop()

json_data = st.session_state.get('json_output', {})
yaml_data = st.session_state.get('yaml_output', {})

st.markdown("---")

# API Overview
st.markdown("## 📡 API Overview")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### Purpose
    This API enables provider software systems to:
    - Retrieve current NDIS pricing
    - Validate support item numbers
    - Check claiming rules
    - Get state-specific pricing
    - Automate claiming validation
    """)

with col2:
    st.markdown("""
    ### Benefits
    - **No manual updates** - Always current pricing
    - **Automated validation** - Reduce claiming errors
    - **Real-time pricing** - Check prices before quotes
    - **Multi-state support** - All Australian states
    - **Rule checking** - Validate before submission
    """)

st.markdown("---")

# API Endpoints Documentation
st.markdown("## 🔗 API Endpoints")

# Endpoint 1: Get Support Item
with st.expander("📌 GET /api/v1/support-items/{item_number}", expanded=True):
    st.markdown("### Get Support Item Details")
    st.markdown("Retrieve complete information for a specific support item.")
    
    st.markdown("#### Request")
    st.code("""
GET /api/v1/support-items/01_001_0117_1_3
Headers:
  Authorization: Bearer YOUR_API_KEY
  Content-Type: application/json
    """, language="http")
    
    st.markdown("#### Response")
    
    # Get example support item
    support_items = json_data.get('support_items', [])
    if support_items:
        example_item = support_items[0]
        
        response_example = {
            "status": "success",
            "data": {
                "support_item_number": example_item.get('support_item_number'),
                "support_item_name": example_item.get('support_item_name'),
                "support_category": example_item.get('support_category'),
                "registration_group": example_item.get('registration_group'),
                "unit": example_item.get('unit'),
                "quote_required": example_item.get('quote_required'),
                "price_limits": example_item.get('price_limits', {})
            }
        }
        
        st.json(response_example)
    
    st.markdown("#### Status Codes")
    st.markdown("""
    - `200 OK` - Support item found
    - `404 Not Found` - Support item doesn't exist
    - `401 Unauthorized` - Invalid API key
    """)

# Endpoint 2: Get Price by State
with st.expander("💰 GET /api/v1/pricing/{item_number}/{state}"):
    st.markdown("### Get State-Specific Pricing")
    st.markdown("Retrieve price for a specific support item in a specific state.")
    
    st.markdown("#### Request")
    st.code("""
GET /api/v1/pricing/01_001_0117_1_3/NSW
Headers:
  Authorization: Bearer YOUR_API_KEY
    """, language="http")
    
    st.markdown("#### Response")
    
    if support_items:
        example_item = support_items[0]
        nsw_price = example_item.get('price_limits', {}).get('NSW', {})
        
        response_example = {
            "status": "success",
            "data": {
                "support_item_number": example_item.get('support_item_number'),
                "support_item_name": example_item.get('support_item_name'),
                "state": "NSW",
                "price": nsw_price.get('price', 0),
                "unit": example_item.get('unit'),
                "effective_date": "2024-07-01",
                "quote_required": example_item.get('quote_required')
            }
        }
        
        st.json(response_example)

# Endpoint 3: Search Support Items
with st.expander("🔍 GET /api/v1/support-items/search"):
    st.markdown("### Search Support Items")
    st.markdown("Search for support items by category, name, or registration group.")
    
    st.markdown("#### Request")
    st.code("""
GET /api/v1/support-items/search?category=Assistance+With+Daily+Life&state=NSW
Headers:
  Authorization: Bearer YOUR_API_KEY
    """, language="http")
    
    st.markdown("#### Query Parameters")
    st.markdown("""
    - `category` - Filter by support category
    - `state` - Filter by state for pricing
    - `registration_group` - Filter by registration group
    - `quote_required` - Filter by quote requirement (true/false)
    - `limit` - Maximum results (default: 50)
    - `offset` - Pagination offset (default: 0)
    """)
    
    st.markdown("#### Response")
    
    if support_items:
        search_results = support_items[:3]  # First 3 items
        
        response_example = {
            "status": "success",
            "total": len(support_items),
            "returned": 3,
            "data": [
                {
                    "support_item_number": item.get('support_item_number'),
                    "support_item_name": item.get('support_item_name'),
                    "support_category": item.get('support_category'),
                    "registration_group": item.get('registration_group')
                }
                for item in search_results
            ]
        }
        
        st.json(response_example)

# Endpoint 4: Validate Claim
with st.expander("✅ POST /api/v1/validate-claim"):
    st.markdown("### Validate Claim Before Submission")
    st.markdown("Check if a claim meets all business rules before submitting to NDIA.")
    
    st.markdown("#### Request")
    st.code("""
POST /api/v1/validate-claim
Headers:
  Authorization: Bearer YOUR_API_KEY
  Content-Type: application/json

Body:
{
  "support_item_number": "01_001_0117_1_3",
  "state": "NSW",
  "quantity": 2,
  "unit_price": 193.99,
  "provider_registration": "0123456789",
  "service_date": "2024-11-30"
}
    """, language="json")
    
    st.markdown("#### Response (Valid Claim)")
    st.json({
        "status": "success",
        "valid": True,
        "data": {
            "support_item_number": "01_001_0117_1_3",
            "support_item_name": "Occupational Therapy - Standard",
            "state": "NSW",
            "current_price": 193.99,
            "claimed_price": 193.99,
            "price_valid": True,
            "quote_required": False,
            "checks_passed": [
                "Price matches current rate",
                "Provider registered",
                "No quote required for this item",
                "Service date within valid range"
            ]
        }
    })
    
    st.markdown("#### Response (Invalid Claim)")
    st.json({
        "status": "error",
        "valid": False,
        "errors": [
            {
                "code": "PRICE_MISMATCH",
                "message": "Claimed price $250.00 exceeds maximum price $193.99 for NSW",
                "field": "unit_price"
            },
            {
                "code": "QUOTE_REQUIRED",
                "message": "This support item requires a quote to be submitted",
                "field": "quote_reference"
            }
        ]
    })

# Endpoint 5: Get Claiming Rules
with st.expander("📋 GET /api/v1/claiming-rules/{rule_name}"):
    st.markdown("### Get Claiming Rules")
    st.markdown("Retrieve business rules for claiming specific support types.")
    
    st.markdown("#### Request")
    st.code("""
GET /api/v1/claiming-rules/therapy_supports
Headers:
  Authorization: Bearer YOUR_API_KEY
    """, language="http")
    
    st.markdown("#### Response")
    
    claiming_rules = yaml_data.get('claiming_rules', {})
    if claiming_rules:
        rule_name = list(claiming_rules.keys())[0] if claiming_rules else 'therapy_supports'
        rule_content = claiming_rules.get(rule_name, {})
        
        response_example = {
            "status": "success",
            "data": {
                "rule_name": rule_name,
                "description": "Rules for claiming therapy and allied health supports",
                "rules": rule_content
            }
        }
        
        st.json(response_example)

st.markdown("---")

# Code Examples
st.markdown("## 💻 Code Examples")

tab1, tab2, tab3, tab4 = st.tabs(["Python", "JavaScript", "PHP", "cURL"])

with tab1:
    st.markdown("### Python Example")
    st.code("""
import requests

API_KEY = "your_api_key_here"
BASE_URL = "https://api.ndis-papl.gov.au/v1"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Get support item
response = requests.get(
    f"{BASE_URL}/support-items/01_001_0117_1_3",
    headers=headers
)

if response.status_code == 200:
    data = response.json()
    print(f"Support: {data['data']['support_item_name']}")
    print(f"Price (NSW): ${data['data']['price_limits']['NSW']['price']}")
else:
    print(f"Error: {response.status_code}")

# Validate claim
claim_data = {
    "support_item_number": "01_001_0117_1_3",
    "state": "NSW",
    "quantity": 2,
    "unit_price": 193.99
}

validation = requests.post(
    f"{BASE_URL}/validate-claim",
    headers=headers,
    json=claim_data
)

if validation.json()['valid']:
    print("✓ Claim is valid")
else:
    print("✗ Claim has errors:")
    for error in validation.json()['errors']:
        print(f"  - {error['message']}")
    """, language="python")

with tab2:
    st.markdown("### JavaScript/Node.js Example")
    st.code("""
const axios = require('axios');

const API_KEY = 'your_api_key_here';
const BASE_URL = 'https://api.ndis-papl.gov.au/v1';

const headers = {
    'Authorization': `Bearer ${API_KEY}`,
    'Content-Type': 'application/json'
};

// Get support item
async function getSupportItem(itemNumber) {
    try {
        const response = await axios.get(
            `${BASE_URL}/support-items/${itemNumber}`,
            { headers }
        );
        
        console.log(`Support: ${response.data.data.support_item_name}`);
        console.log(`Price (NSW): $${response.data.data.price_limits.NSW.price}`);
        
        return response.data;
    } catch (error) {
        console.error('Error:', error.response.status);
    }
}

// Validate claim
async function validateClaim(claimData) {
    try {
        const response = await axios.post(
            `${BASE_URL}/validate-claim`,
            claimData,
            { headers }
        );
        
        if (response.data.valid) {
            console.log('✓ Claim is valid');
        } else {
            console.log('✗ Claim has errors:');
            response.data.errors.forEach(error => {
                console.log(`  - ${error.message}`);
            });
        }
        
        return response.data;
    } catch (error) {
        console.error('Error:', error.response.status);
    }
}

// Usage
getSupportItem('01_001_0117_1_3');
    """, language="javascript")

with tab3:
    st.markdown("### PHP Example")
    st.code("""
<?php

$apiKey = 'your_api_key_here';
$baseUrl = 'https://api.ndis-papl.gov.au/v1';

$headers = [
    'Authorization: Bearer ' . $apiKey,
    'Content-Type: application/json'
];

// Get support item
function getSupportItem($itemNumber, $baseUrl, $headers) {
    $ch = curl_init($baseUrl . '/support-items/' . $itemNumber);
    curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    
    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    if ($httpCode == 200) {
        $data = json_decode($response, true);
        echo "Support: " . $data['data']['support_item_name'] . "\\n";
        echo "Price (NSW): $" . $data['data']['price_limits']['NSW']['price'] . "\\n";
        return $data;
    } else {
        echo "Error: " . $httpCode . "\\n";
        return null;
    }
}

// Validate claim
function validateClaim($claimData, $baseUrl, $headers) {
    $ch = curl_init($baseUrl . '/validate-claim');
    curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($claimData));
    
    $response = curl_exec($ch);
    curl_close($ch);
    
    $data = json_decode($response, true);
    
    if ($data['valid']) {
        echo "✓ Claim is valid\\n";
    } else {
        echo "✗ Claim has errors:\\n";
        foreach ($data['errors'] as $error) {
            echo "  - " . $error['message'] . "\\n";
        }
    }
    
    return $data;
}

// Usage
getSupportItem('01_001_0117_1_3', $baseUrl, $headers);

?>
    """, language="php")

with tab4:
    st.markdown("### cURL Examples")
    st.code("""
# Get support item
curl -X GET "https://api.ndis-papl.gov.au/v1/support-items/01_001_0117_1_3" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json"

# Get pricing for NSW
curl -X GET "https://api.ndis-papl.gov.au/v1/pricing/01_001_0117_1_3/NSW" \\
  -H "Authorization: Bearer YOUR_API_KEY"

# Search support items
curl -X GET "https://api.ndis-papl.gov.au/v1/support-items/search?category=Assistance+With+Daily+Life&state=NSW" \\
  -H "Authorization: Bearer YOUR_API_KEY"

# Validate claim
curl -X POST "https://api.ndis-papl.gov.au/v1/validate-claim" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "support_item_number": "01_001_0117_1_3",
    "state": "NSW",
    "quantity": 2,
    "unit_price": 193.99,
    "provider_registration": "0123456789",
    "service_date": "2024-11-30"
  }'

# Get claiming rules
curl -X GET "https://api.ndis-papl.gov.au/v1/claiming-rules/therapy_supports" \\
  -H "Authorization: Bearer YOUR_API_KEY"
    """, language="bash")

st.markdown("---")

# Authentication
st.markdown("## 🔐 Authentication")

st.markdown("""
### API Key Authentication

All API requests require a valid API key in the Authorization header:

```
Authorization: Bearer YOUR_API_KEY
```

**To obtain an API key:**
1. Register your provider organization
2. Complete provider verification
3. Request API access through NDIA portal
4. Receive API key via secure channel

**Security best practices:**
- ✅ Store API keys securely (environment variables, key vault)
- ✅ Never commit API keys to version control
- ✅ Rotate API keys every 90 days
- ✅ Use separate keys for development and production
- ✅ Implement rate limiting in your application
- ⚠️ Never share API keys
- ⚠️ Never log API keys in application logs
""")

st.markdown("---")

# Rate Limits
st.markdown("## ⚡ Rate Limits")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Requests per Minute", "100")
    st.caption("Standard tier")

with col2:
    st.metric("Requests per Hour", "5,000")
    st.caption("Standard tier")

with col3:
    st.metric("Requests per Day", "100,000")
    st.caption("Standard tier")

st.markdown("""
**Rate limit headers in response:**
- `X-RateLimit-Limit` - Maximum requests allowed
- `X-RateLimit-Remaining` - Requests remaining in current window
- `X-RateLimit-Reset` - Time when the limit resets (Unix timestamp)

**When rate limit exceeded:**
- Status Code: `429 Too Many Requests`
- Retry-After header indicates when to retry
""")

st.markdown("---")

# Error Handling
st.markdown("## ⚠️ Error Handling")

st.markdown("### Standard Error Response")

st.code("""
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request failed validation",
    "details": [
      {
        "field": "unit_price",
        "message": "Price exceeds maximum allowed for this state"
      }
    ]
  },
  "timestamp": "2024-11-30T12:34:56Z",
  "request_id": "req_abc123xyz"
}
""", language="json")

st.markdown("### Error Codes")

error_codes = {
    "400 Bad Request": "Invalid request format or parameters",
    "401 Unauthorized": "Missing or invalid API key",
    "403 Forbidden": "API key doesn't have required permissions",
    "404 Not Found": "Requested resource doesn't exist",
    "422 Unprocessable Entity": "Request validation failed",
    "429 Too Many Requests": "Rate limit exceeded",
    "500 Internal Server Error": "Server error - contact support",
    "503 Service Unavailable": "API temporarily unavailable"
}

for code, description in error_codes.items():
    st.markdown(f"**{code}:** {description}")

st.markdown("---")

# Benefits
st.markdown("## 💡 Benefits of API Integration")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### For Providers
    - **No manual updates** - Always current pricing
    - **Reduce errors** - Automated validation before claiming
    - **Save time** - No PDF searching
    - **Real-time pricing** - Check before quoting
    - **Multi-state** - All states in one API
    - **Automated compliance** - Rules built-in
    """)

with col2:
    st.markdown("""
    ### For NDIA
    - **Reduce claiming errors** - Validation before submission
    - **Lower support costs** - Fewer query calls
    - **Better data quality** - Standardized submissions
    - **Audit trail** - Track API usage
    - **Version control** - Manage pricing updates centrally
    - **Analytics** - Usage insights
    """)

st.markdown("---")

# Support
st.markdown("## 🆘 Support")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### Documentation
    - [API Reference](https://docs.ndis-papl.gov.au/api)
    - [Getting Started Guide](https://docs.ndis-papl.gov.au/quickstart)
    - [Authentication Guide](https://docs.ndis-papl.gov.au/auth)
    - [Best Practices](https://docs.ndis-papl.gov.au/best-practices)
    """)

with col2:
    st.markdown("""
    ### Contact
    - **Email:** api-support@ndis.gov.au
    - **Phone:** 1800 800 110
    - **Status:** status.ndis-papl.gov.au
    - **Community:** forum.ndis-papl.gov.au
    """)

st.markdown("---")

# Download API Spec
st.markdown("## 📥 Download API Specification")

col1, col2 = st.columns(2)

with col1:
    # OpenAPI spec
    openapi_spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "NDIS PAPL API",
            "version": "1.0.0",
            "description": "REST API for NDIS Pricing Arrangements and Price Limits"
        },
        "servers": [
            {"url": "https://api.ndis-papl.gov.au/v1"}
        ],
        "paths": {
            "/support-items/{item_number}": {
                "get": {
                    "summary": "Get support item details",
                    "parameters": [
                        {
                            "name": "item_number",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"}
                        }
                    ]
                }
            }
        }
    }
    
    if st.download_button(
        "📄 Download OpenAPI Spec (JSON)",
        data=json.dumps(openapi_spec, indent=2),
        file_name="ndis-papl-api-spec.json",
        mime="application/json"
    ):
        st.success("✓ OpenAPI specification downloaded!")

with col2:
    # Postman collection
    postman_collection = {
        "info": {
            "name": "NDIS PAPL API",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": [
            {
                "name": "Get Support Item",
                "request": {
                    "method": "GET",
                    "header": [
                        {"key": "Authorization", "value": "Bearer {{API_KEY}}"}
                    ],
                    "url": {
                        "raw": "{{BASE_URL}}/support-items/01_001_0117_1_3",
                        "host": ["{{BASE_URL}}"],
                        "path": ["support-items", "01_001_0117_1_3"]
                    }
                }
            }
        ]
    }
    
    if st.download_button(
        "📮 Download Postman Collection",
        data=json.dumps(postman_collection, indent=2),
        file_name="ndis-papl-postman-collection.json",
        mime="application/json"
    ):
        st.success("✓ Postman collection downloaded!")

st.markdown("---")

st.info("""
💡 **Note:** This is a demonstration of what a Provider API could look like. 
The actual implementation would require NDIA infrastructure, authentication systems, 
and integration with existing NDIA services. Contact NDIA Markets Delivery for production deployment.
""")

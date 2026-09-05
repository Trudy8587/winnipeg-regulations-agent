# API Keys & Environment Setup Guide

## 🔐 Getting Your API Keys

This guide walks you through obtaining all necessary API keys and configuring your environment.

---

## 1. OpenAI API Key

### Step 1: Create OpenAI Account
1. Go to [https://platform.openai.com/signup](https://platform.openai.com/signup)
2. Sign up with your email or Google/Microsoft account
3. Verify your email

### Step 2: Create API Key
1. Go to [https://platform.openai.com/api/keys](https://platform.openai.com/api/keys)
2. Click **"Create new secret key"**
3. Copy the key immediately (it won't be shown again)
4. **Store it safely** (we'll use it in step 3)

### Step 3: Set Up Billing
1. Go to [https://platform.openai.com/account/billing/overview](https://platform.openai.com/account/billing/overview)
2. Add a payment method
3. Set up usage limits to avoid unexpected charges:
   - Click **"Usage limits"**
   - Set a monthly budget (e.g., $20/month for testing)

### Pricing Reference
- **GPT-4**: ~$0.03 per 1K prompt tokens, ~$0.06 per 1K completion tokens
- **Embeddings (text-embedding-3-small)**: ~$0.02 per 1M tokens
- For typical queries: ~$0.01-0.05 per query

---

## 2. Pinecone API Key (Vector Database)

### Step 1: Create Pinecone Account
1. Go to [https://www.pinecone.io/](https://www.pinecone.io/)
2. Click **"Sign up free"**
3. Sign up with email or Google account
4. Create organization

### Step 2: Create API Key
1. After login, go to **"API Keys"** in left sidebar
2. Click **"Create API Key"**
3. Name it: `winnipeg-agent-prod`
4. Copy the API key
5. Copy the environment name (e.g., `gcp-starter`)

### Step 3: Create Index
1. Go to **"Indexes"** in left sidebar
2. Click **"Create Index"**
3. Configure:
   - **Name**: `winnipeg-regulations`
   - **Dimension**: `1536` (for OpenAI embeddings)
   - **Metric**: `cosine`
   - **Pod type**: `starter` (free tier)
4. Click **"Create Index"**
5. Wait for index to be ready (usually 1-2 minutes)

### Free Tier Limits
- 1 million vectors
- 1 index
- Perfect for development and testing

---

## 3. Configure `.env` File

### Step 1: Copy Template
```bash
cp .env.example .env
```

### Step 2: Edit `.env` with Your Keys

Open `.env` in your text editor and fill in the values:

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False

# OpenAI Configuration
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxx  # Your OpenAI key here
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.1

# Pinecone Configuration
PINECONE_API_KEY=xxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxx  # Your Pinecone key here
PINECONE_ENVIRONMENT=gcp-starter                      # Your Pinecone environment
PINECONE_INDEX_NAME=winnipeg-regulations              # Index name you created

# Database Configuration
DATABASE_URL=sqlite:///./winnipeg_agent.db             # Or use PostgreSQL

# Logging
LOG_LEVEL=INFO

# Agent Configuration
AGENT_NAME=Winnipeg Regulations Assistant
AGENT_DESCRIPTION=AI-powered assistant for Winnipeg by-laws and Manitoba regulations
```

### Step 3: Verify Your Keys

```bash
# Check that .env file exists and is not empty
cat .env

# Make sure .env is in .gitignore (it already is)
grep .env .gitignore
```

### ⚠️ Security Best Practices

**DO:**
- ✅ Keep `.env` file locally only
- ✅ Never commit `.env` to Git
- ✅ Rotate API keys regularly
- ✅ Use different keys for dev/prod
- ✅ Set usage limits on API accounts
- ✅ Monitor API usage and costs

**DON'T:**
- ❌ Share your API keys publicly
- ❌ Commit `.env` to version control
- ❌ Include keys in code comments
- ❌ Use same keys across environments
- ❌ Leave debug mode enabled in production

---

## 4. Test Your Configuration

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run Configuration Test
```bash
# Create a test script
cat > test_config.py << 'EOF'
import os
from dotenv import load_dotenv

load_dotenv()

print("✓ Configuration Test")
print("-" * 50)

# Check OpenAI
openai_key = os.getenv("OPENAI_API_KEY")
print(f"✓ OPENAI_API_KEY: {'Set' if openai_key else 'MISSING'}")
print(f"  Key starts with: sk-proj-...")

openai_model = os.getenv("OPENAI_MODEL")
print(f"✓ OPENAI_MODEL: {openai_model}")

# Check Pinecone
pinecone_key = os.getenv("PINECONE_API_KEY")
print(f"✓ PINECONE_API_KEY: {'Set' if pinecone_key else 'MISSING'}")

pinecone_env = os.getenv("PINECONE_ENVIRONMENT")
print(f"✓ PINECONE_ENVIRONMENT: {pinecone_env}")

pinecone_index = os.getenv("PINECONE_INDEX_NAME")
print(f"✓ PINECONE_INDEX_NAME: {pinecone_index}")

# Check Database
db_url = os.getenv("DATABASE_URL")
print(f"✓ DATABASE_URL: {'Set' if db_url else 'MISSING'}")

print("-" * 50)
print("✓ All configurations loaded successfully!")
EOF

python test_config.py
```

### Step 3: Test OpenAI Connection
```bash
cat > test_openai.py << 'EOF'
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

try:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is Winnipeg known for?"}
        ],
        max_tokens=100
    )
    print("✓ OpenAI Connection: SUCCESS")
    print(f"Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"✗ OpenAI Connection: FAILED")
    print(f"Error: {e}")
EOF

python test_openai.py
```

### Step 4: Test Pinecone Connection
```bash
cat > test_pinecone.py << 'EOF'
import os
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

try:
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    
    # List indexes
    indexes = pc.list_indexes()
    print("✓ Pinecone Connection: SUCCESS")
    print(f"Available indexes: {indexes}")
    
    # Get index info
    index_name = os.getenv("PINECONE_INDEX_NAME")
    if index_name:
        index = pc.Index(index_name)
        stats = index.describe_index_stats()
        print(f"✓ Index '{index_name}': Ready")
        print(f"  Namespaces: {stats}")
except Exception as e:
    print(f"✗ Pinecone Connection: FAILED")
    print(f"Error: {e}")
EOF

python test_pinecone.py
```

### Step 5: Start the API Server
```bash
python -m uvicorn src.api.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Uvicorn reloading on file change
```

### Step 6: Test the API
Open your browser to: **http://localhost:8000/docs**

This opens the interactive Swagger UI where you can test endpoints directly.

---

## 5. Environment Variables Reference

| Variable | Type | Required | Example |
|----------|------|----------|---------|
| `OPENAI_API_KEY` | String | Yes | `sk-proj-...` |
| `OPENAI_MODEL` | String | No | `gpt-4` |
| `OPENAI_TEMPERATURE` | Float | No | `0.1` |
| `PINECONE_API_KEY` | String | Yes | `xxxxxxx-xxxx...` |
| `PINECONE_ENVIRONMENT` | String | Yes | `gcp-starter` |
| `PINECONE_INDEX_NAME` | String | Yes | `winnipeg-regulations` |
| `DATABASE_URL` | String | No | `sqlite:///./test.db` |
| `API_HOST` | String | No | `0.0.0.0` |
| `API_PORT` | Integer | No | `8000` |
| `LOG_LEVEL` | String | No | `INFO` |
| `DEBUG` | Boolean | No | `False` |

---

## 6. Troubleshooting

### OpenAI Issues

**Error: `AuthenticationError: Incorrect API key provided`**
- ✓ Check your API key is correct (starts with `sk-proj-`)
- ✓ Verify key hasn't been revoked on OpenAI dashboard
- ✓ Check for extra spaces in `.env`

**Error: `RateLimitError: Rate limit exceeded`**
- ✓ Check your usage limits at https://platform.openai.com/account/billing/limits
- ✓ Reduce `OPENAI_TEMPERATURE` for more consistent responses
- ✓ Add delays between requests

**Error: `InvalidRequestError: The model gpt-4 does not exist`**
- ✓ Ensure you have GPT-4 API access (requires paid account)
- ✓ Try `gpt-3.5-turbo` as alternative (cheaper)
- ✓ Check supported models: https://platform.openai.com/docs/models

### Pinecone Issues

**Error: `PineconeException: Index not found`**
- ✓ Verify index name matches exactly in `.env`
- ✓ Check index was created successfully
- ✓ Ensure API key has permission to access index

**Error: `Connection timeout`**
- ✓ Check Pinecone status page: https://status.pinecone.io/
- ✓ Verify internet connection
- ✓ Try again in a few minutes

### Database Issues

**Error: `sqlite3.OperationalError: unable to open database file`**
- ✓ Check directory exists
- ✓ Ensure write permissions
- ✓ Or use PostgreSQL for production

---

## 7. Production Deployment

For production, store API keys in secure vaults:

### AWS
```bash
aws secretsmanager create-secret \
  --name winnipeg-agent-keys \
  --secret-string '{"OPENAI_API_KEY":"...","PINECONE_API_KEY":"..."}'
```

### Google Cloud
```bash
gcloud secrets create openai-key --data-file=-
gcloud secrets create pinecone-key --data-file=-
```

### Azure
```bash
az keyvault secret set --vault-name winnipeg-vault \
  --name openai-key --value YOUR_KEY
```

---

## ✅ Checklist

Before proceeding with data loading:

- [ ] OpenAI account created and verified
- [ ] OpenAI API key generated
- [ ] OpenAI billing configured with usage limits
- [ ] Pinecone account created
- [ ] Pinecone API key generated
- [ ] Pinecone index created (`winnipeg-regulations`)
- [ ] `.env` file created with all keys
- [ ] `.env` file added to `.gitignore` ✓
- [ ] Configuration test passed
- [ ] OpenAI connection test passed
- [ ] Pinecone connection test passed
- [ ] API server starts successfully

---

## 📚 Next Steps

Once your API keys are configured:

1. **Test the API** → Open http://localhost:8000/docs
2. **Load Regulation Data** → See [DATA_LOADING.md](./DATA_LOADING.md)
3. **Test Agent Queries** → Query the API with sample questions
4. **Deploy to Production** → See [DEPLOYMENT.md](./DEPLOYMENT.md)

---

## 📞 Support

**OpenAI Support**: https://help.openai.com/
**Pinecone Support**: https://support.pinecone.io/
**Project Issues**: https://github.com/Trudy8587/winnipeg-regulations-agent/issues

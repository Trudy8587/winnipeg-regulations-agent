# Data Loading Guide

## Overview

This guide explains how to prepare and load regulation data into the Winnipeg Regulations Agent.

## Data Format

Regulations should be stored in JSON format with the following structure:

```json
{
  "regulations": [
    {
      "id": "WBL-2024-001",
      "title": "Business Licensing By-law",
      "section": "3.0",
      "subsection": "3.2.1",
      "text": "Full regulation text here...",
      "category": "business",
      "effective_date": "2024-01-01",
      "source_url": "https://winnipeg.ca/bylaws/",
      "tags": ["business", "license", "permit"]
    }
  ]
}
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | Yes | Unique regulation identifier (e.g., WBL-2024-001) |
| title | string | Yes | Regulation title |
| section | string | Yes | Primary section number |
| subsection | string | No | Subsection identifier |
| text | string | Yes | Full regulation text |
| category | string | Yes | Category for filtering (business, zoning, permits, compliance, accessibility) |
| effective_date | string | Yes | Effective date (YYYY-MM-DD) |
| source_url | string | Yes | Link to official source |
| tags | array | No | List of tags for search optimization |

## Data Sources

### Winnipeg By-laws
- **Official Source**: https://winnipeg.ca/bylaws/
- **Key By-laws to Include**:
  - Business Licensing By-law (#6500/1)
  - Zoning By-law (#8000/2)
  - Building and Construction By-law
  - Property Maintenance By-law
  - Noise By-law
  - Off-Street Parking By-law
  - Signage By-law

### Manitoba Regulations
- **Official Source**: https://gov.mb.ca/justice/
- **Key Regulations to Include**:
  - Employment Standards Act
  - Workplace Health and Safety Regulation
  - Human Rights Code
  - Accessibility Act

## Preparing Data

### Step 1: Gather Regulation Documents

Download or access official documents from:
- City of Winnipeg website
- Manitoba Justice website
- City/Provincial archives

### Step 2: Parse into JSON

Create a JSON file with regulations structured according to the format above.

**Example Structure:**
```
data/regulations/
├── winnipeg_bylaws.json
├── manitoba_regulations.json
└── sample_regulations.json
```

### Step 3: Add to Repository

```bash
# Copy your regulation files to the data directory
cp your_regulations.json data/regulations/

# Or create new files directly
cat > data/regulations/custom_bylaws.json << 'EOF'
{
  "regulations": [
    {
      "id": "WBL-2024-XXX",
      "title": "Your By-law Title",
      ...
    }
  ]
}
EOF
```

## Loading Data

### Step 1: Verify Configuration

```bash
python scripts/validate_config.py
```

### Step 2: Run Data Loader

```bash
python scripts/load_regulations.py
```

This script will:
1. Read all JSON files from `data/regulations/`
2. Create embeddings using OpenAI API
3. Index in Pinecone vector database
4. Log progress and results

### Expected Output

```
INFO:root:Starting Winnipeg Regulations Data Loader
INFO:root:Loading regulation files from data/regulations
INFO:root:Loading sample_regulations.json
INFO:root:Loaded 12 regulations from sample_regulations.json
INFO:root:Total regulations loaded: 12
INFO:root:Indexing 12 regulations in Pinecone
INFO:root:Upserting batch of 12 vectors...
INFO:root:✓ Data loading complete!
INFO:root:  - Total regulations indexed: 12
INFO:root:  - Pinecone index: winnipeg-regulations
```

## Batch Processing Large Datasets

For large datasets (1000+ regulations):

```python
# Modify load_regulations.py to process in chunks
python scripts/load_regulations.py --batch-size 500
```

## Updating Existing Regulations

To update regulations that are already indexed:

```bash
# The load script will replace existing vectors with same ID
python scripts/load_regulations.py
```

Vectors are identified by: `{id}-{section}-{subsection}`

## Verification

### Verify Data in Pinecone

```bash
python << 'EOF'
from pinecone import Pinecone
import os
from dotenv import load_dotenv

load_dotenv()
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))
stats = index.describe_index_stats()
print(f"Total vectors: {stats['total_vector_count']}")
print(f"Namespaces: {stats['namespaces']}")
EOF
```

### Test Search

```bash
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What permits do I need to open a restaurant?"
  }'
```

## Troubleshooting

### Issue: "No regulations loaded"
- **Check**: Data files exist in `data/regulations/`
- **Fix**: Verify JSON format is correct
- **Validate**: `python -m json.tool data/regulations/sample_regulations.json`

### Issue: "Rate limit exceeded" (OpenAI)
- **Check**: API usage on https://platform.openai.com/account/billing/limits
- **Fix**: Wait or set lower batch size
- **Optimize**: Use fewer, larger chunks instead of many small ones

### Issue: "Index not found" (Pinecone)
- **Check**: Index name in `.env` matches Pinecone
- **Fix**: Create index if missing: `PINECONE_INDEX_NAME=winnipeg-regulations`

### Issue: Embeddings are slow
- **Cause**: Creating individual embeddings per regulation
- **Solution**: Batch embeddings in groups of 20-50
- **Reference**: See OpenAI batch processing docs

## Cost Optimization

### Embedding Costs (OpenAI)
- text-embedding-3-small: $0.02 per 1M tokens
- ~500 tokens per regulation (average)
- 1000 regulations ≈ $0.01

### Vector Database Costs (Pinecone)
- Free tier: 1M vectors, 1 index
- Production: Pay-as-you-go

## Best Practices

1. **Organize by Source**: Keep Winnipeg and Manitoba regulations in separate files
2. **Include Metadata**: Always populate title, section, and source_url
3. **Add Tags**: Use tags to help search and categorization
4. **Version Control**: Track regulation versions in effective_date
5. **Regular Updates**: Set up automated updates for new/changed regulations
6. **Test Before Deploy**: Validate data with test queries before production

## Automation

### Set Up Periodic Updates

Create a cron job (Linux/Mac):

```bash
# Update regulations weekly
0 0 * * 0 cd /path/to/winnipeg-regulations-agent && python scripts/load_regulations.py
```

Or using GitHub Actions:

```yaml
name: Update Regulations
on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Monday
jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Load regulations
        run: python scripts/load_regulations.py
```

## Next Steps

1. ✅ Prepare regulation data files
2. ✅ Run `python scripts/load_regulations.py`
3. ✅ Verify data with test queries
4. ✅ Deploy agent to production
5. ✅ Set up periodic updates

See [SETUP.md](./SETUP.md) for environment configuration.

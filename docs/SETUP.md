# Setup Guide

## Prerequisites

- Python 3.9 or higher
- pip package manager
- Git
- OpenAI API key (or alternative LLM provider)
- Pinecone account (for vector database)

## Step-by-Step Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Trudy8587/winnipeg-regulations-agent.git
cd winnipeg-regulations-agent
```

### 2. Create Virtual Environment

```bash
# On Linux/Mac
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your API keys
nano .env  # or use your preferred editor
```

#### Required Environment Variables:

- `OPENAI_API_KEY`: Get from https://platform.openai.com/
- `PINECONE_API_KEY`: Get from https://www.pinecone.io/
- `PINECONE_ENVIRONMENT`: Pinecone environment name (e.g., gcp-starter)
- `PINECONE_INDEX_NAME`: Name of your Pinecone index

### 5. Verify Installation

```bash
# Run tests
pytest

# Or run API in test mode
python -m uvicorn src.api.main:app --reload
```

## Running the Agent

### Start the API Server

```bash
python -m uvicorn src.api.main:app --reload
```

The API will be available at: `http://localhost:8000`

### Interactive API Documentation

Open your browser to: `http://localhost:8000/docs`

This provides an interactive Swagger UI where you can test endpoints directly.

### Example Queries

Using curl:

```bash
# Business license query
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What permits do I need to open a restaurant in Winnipeg?",
    "category": "business"
  }'

# Zoning query
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Can I build a secondary suite on my property?"
  }'

# Compliance check
curl -X POST "http://localhost:8000/api/compliance?activity_type=retail"
```

## Docker Setup

### Build Docker Image

```bash
docker build -f docker/Dockerfile -t winnipeg-agent .
```

### Run Docker Container

```bash
docker run -p 8000:8000 --env-file .env winnipeg-agent
```

## Data Setup

### 1. Prepare Regulation Data

Create a JSON file with regulations in `data/regulations/`:

```json
{
  "regulations": [
    {
      "id": "WBL-2024-001",
      "title": "Business Licensing By-law",
      "section": "3.2.1",
      "subsection": "a",
      "text": "Every person operating a restaurant shall obtain a business license...",
      "category": "business",
      "effective_date": "2024-01-01",
      "source_url": "https://winnipeg.ca/..."
    }
  ]
}
```

### 2. Load Regulations

```bash
python scripts/load_regulations.py
```

This script will:
- Read regulation files
- Create embeddings
- Index in Pinecone
- Store metadata in database

## Testing

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=src
```

### Run Specific Test File

```bash
pytest tests/test_api.py
```

## Troubleshooting

### API Key Issues

```
Error: OPENAI_API_KEY environment variable is required
Solution: Make sure .env file exists and has OPENAI_API_KEY set
```

### Connection Issues

```
Error: Could not connect to Pinecone
Solution: Verify PINECONE_API_KEY and PINECONE_ENVIRONMENT are correct
```

### Port Already in Use

```
Error: Address already in use
Solution: Kill process on port 8000 or use different port:
python -m uvicorn src.api.main:app --port 8001
```

## Next Steps

1. **Load Regulations**: Prepare and load Winnipeg by-laws and Manitoba regulations
2. **Configure Retriever**: Set up vector database and fine-tune search
3. **Test Agent**: Run tests and validate responses
4. **Deploy**: Push to production (AWS, GCP, Azure)
5. **Monitor**: Set up logging and monitoring

See [ARCHITECTURE.md](./ARCHITECTURE.md) for more details on system design.

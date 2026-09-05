# Testing Guide

## Overview

This guide covers testing the Winnipeg Regulations Agent.

## Unit Tests

Run all unit tests:

```bash
pytest tests/
```

Run specific test file:

```bash
pytest tests/test_api.py
```

Run with coverage:

```bash
pytest --cov=src tests/
```

## Integration Tests

Test the full agent workflow:

```bash
pytest tests/test_agent.py -v
```

## Manual Testing

### 1. Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "agent": "Winnipeg Regulations Assistant",
  "version": "0.1.0"
}
```

### 2. API Documentation

Open browser: `http://localhost:8000/docs`

This provides interactive Swagger UI for testing.

### 3. Test Queries

#### Business Query

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What permits do I need to open a restaurant in Winnipeg?",
    "category": "business"
  }'
```

#### Zoning Query

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Can I build a secondary suite on my property?"
  }'
```

#### Compliance Query

```bash
curl -X POST http://localhost:8000/api/compliance \
  -H "Content-Type: application/json" \
  -d 'activity_type=restaurant'
```

## Test Scenarios

### Scenario 1: Restaurant Opening

Queries to test:
- "What permits do I need to open a restaurant?"
- "What health and safety requirements apply?"
- "How much does a business license cost?"
- "What are the hours of operation restrictions?"

Expected: Returns relevant regulations about business licenses, food service, health inspections

### Scenario 2: Secondary Suite

Queries to test:
- "Can I build a secondary suite?"
- "What are the zoning restrictions?"
- "Do I need a permit?"
- "What are the parking requirements?"

Expected: Returns zoning regulations, permit requirements, parking rules

### Scenario 3: Workplace Requirements

Queries to test:
- "What are the minimum wage requirements in Manitoba?"
- "What safety regulations apply?"
- "What accessibility requirements must I comply with?"

Expected: Returns Manitoba employment standards, safety regulations, accessibility requirements

## Performance Testing

### Load Testing

```bash
# Install locust
pip install locust

# Create locustfile.py
cat > locustfile.py << 'EOF'
from locust import HttpUser, task, between

class RegulationUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def search_regulations(self):
        self.client.post("/api/search", json={
            "query": "What permits do I need to open a restaurant?"
        })
EOF

# Run load test
locust -f locustfile.py --host=http://localhost:8000
```

### Response Time Monitoring

```python
import time
import requests

start = time.time()
response = requests.post('http://localhost:8000/api/search', json={
    'query': 'What permits do I need?'
})
end = time.time()

print(f"Response time: {(end - start) * 1000:.2f}ms")
```

## Debugging

### Enable Debug Mode

In `.env`:
```
DEBUG=True
LOG_LEVEL=DEBUG
```

### View Logs

```bash
# Follow logs in real-time
tail -f logs/agent.log

# Search logs
grep "ERROR" logs/agent.log
```

### Test with Specific Regulations

```python
from src.retrievers import HybridRegulationRetriever

retriever = HybridRegulationRetriever()
results = retriever.retrieve("restaurant permits")
for result in results:
    print(f"ID: {result['id']}")
    print(f"Title: {result['title']}")
    print(f"Score: {result['relevance_score']}")
```

## Continuous Testing

### GitHub Actions

Create `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest --cov=src
```

## Acceptance Criteria

Before deploying to production, verify:

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Response time < 2 seconds
- [ ] 95th percentile response time < 5 seconds
- [ ] API handles 100+ concurrent requests
- [ ] Sample queries return relevant regulations
- [ ] Citations are properly formatted
- [ ] No errors in logs
- [ ] Database queries are optimized
- [ ] API security checks pass

## Troubleshooting

### Test Fails: "Connection refused"
- Make sure API server is running: `python -m uvicorn src.api.main:app --reload`

### Test Fails: "Invalid API key"
- Check `.env` file has valid OpenAI and Pinecone keys
- Run: `python scripts/validate_config.py`

### Test Fails: "Index not found"
- Verify Pinecone index exists
- Check `PINECONE_INDEX_NAME` in `.env`

### Test Slow
- Check network connection to OpenAI/Pinecone
- Review API rate limits
- Check server resources

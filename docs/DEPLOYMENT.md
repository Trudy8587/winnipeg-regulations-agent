# Deployment Guide

## Overview

This guide covers deploying the Winnipeg Regulations Agent to production environments.

## Deployment Options

### Option 1: Local Development

**Best for:** Testing and development

```bash
# Start the server
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 2: Docker (Recommended)

**Best for:** Consistent environments across machines

#### Build Docker Image

```bash
docker build -f docker/Dockerfile -t winnipeg-agent:latest .
```

#### Run Docker Container

```bash
docker run -p 8000:8000 \
  --env-file .env \
  --name winnipeg-agent \
  winnipeg-agent:latest
```

#### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: docker/Dockerfile
    ports:
      - "8000:8000"
    env_file: .env
    restart: unless-stopped
    environment:
      - LOG_LEVEL=INFO
```

Run:
```bash
docker-compose up -d
```

### Option 3: AWS Deployment

#### Option 3A: AWS Lambda + API Gateway

**Best for:** Serverless, pay-per-request

```bash
# Install serverless framework
npm install -g serverless
npm install --save-dev serverless-python-requirements

# Deploy
serverless deploy
```

#### Option 3B: AWS ECS + Fargate

**Best for:** Containerized, scalable

1. Create ECR repository:
```bash
aws ecr create-repository --repository-name winnipeg-agent
```

2. Push Docker image:
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
docker tag winnipeg-agent:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/winnipeg-agent:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/winnipeg-agent:latest
```

3. Create ECS cluster and task definition
4. Create Fargate service

### Option 4: Google Cloud Run

**Best for:** Simple, serverless, auto-scaling

```bash
# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash
gcloud auth login

# Deploy
gcloud run deploy winnipeg-agent \
  --source . \
  --platform managed \
  --region us-central1 \
  --set-env-vars OPENAI_API_KEY=$OPENAI_API_KEY,PINECONE_API_KEY=$PINECONE_API_KEY
```

### Option 5: Heroku

**Best for:** Quick, simple deployment

```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login
heroku login

# Create app
heroku create winnipeg-agent

# Set environment variables
heroku config:set OPENAI_API_KEY=$OPENAI_API_KEY
heroku config:set PINECONE_API_KEY=$PINECONE_API_KEY

# Deploy
git push heroku main
```

### Option 6: DigitalOcean App Platform

**Best for:** Developer-friendly, affordable

1. Connect GitHub repository
2. Configure environment variables
3. Auto-deploy on push

## Environment Configuration

### Production Environment Variables

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False
LOG_LEVEL=INFO

# OpenAI
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.1

# Pinecone
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=gcp-starter
PINECONE_INDEX_NAME=winnipeg-regulations

# Database (PostgreSQL for production)
DATABASE_URL=postgresql://user:password@host:5432/winnipeg_agent

# Agent
AGENT_NAME=Winnipeg Regulations Assistant
AGENT_DESCRIPTION=AI-powered assistant for Winnipeg by-laws and Manitoba regulations
```

## Security Best Practices

### 1. Secret Management

```bash
# AWS Secrets Manager
aws secretsmanager create-secret \
  --name winnipeg-agent-keys \
  --secret-string file://secrets.json

# Google Secret Manager
gcloud secrets create openai-key --data-file=-

# Azure Key Vault
az keyvault secret set --vault-name winnipeg-vault \
  --name openai-key --value YOUR_KEY
```

### 2. API Authentication

Add API key validation:

```python
from fastapi import Header, HTTPException

@app.post("/api/search")
async def search_regulations(
    request: RegulationQuery,
    x_api_key: str = Header(None)
):
    if x_api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API key")
    # ... process request
```

### 3. HTTPS/TLS

Use reverse proxy (nginx) or load balancer:

```nginx
server {
    listen 443 ssl;
    server_name api.winnipeg-regulations.ca;
    
    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 4. Rate Limiting

```bash
# Install slowapi
pip install slowapi
```

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/search")
@limiter.limit("100/minute")
async def search_regulations(request: RegulationQuery):
    # ... process request
```

## Monitoring & Logging

### Application Logging

```python
import logging
import logging.handlers

logger = logging.getLogger(__name__)
logger.addHandler(logging.handlers.RotatingFileHandler(
    'logs/agent.log',
    maxBytes=10485760,  # 10MB
    backupCount=10
))
```

### Cloud Monitoring

**AWS CloudWatch:**
```bash
aws logs create-log-group --log-group-name /winnipeg-agent
aws logs create-log-stream --log-group-name /winnipeg-agent --log-stream-name api
```

**Google Cloud Logging:**
```bash
gcloud logging read "resource.type=cloud_run_revision" --limit 50
```

### Performance Monitoring

Use APM tools:
- **DataDog**: `pip install datadog`
- **New Relic**: `pip install newrelic`
- **Sentry**: `pip install sentry-sdk`

## Scaling

### Horizontal Scaling

```bash
# AWS Auto Scaling
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name winnipeg-agent-asg \
  --launch-configuration-name winnipeg-agent-lc \
  --min-size 2 \
  --max-size 10
```

### Load Balancing

```yaml
# Example with multiple instances
instances:
  - instance_1: http://localhost:8001
  - instance_2: http://localhost:8002
  - instance_3: http://localhost:8003
```

## CI/CD Pipeline

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to production
        run: |
          # Deploy commands here
```

## Cost Optimization

1. **Use Spot Instances**: Save 70% on compute
2. **Auto-scale down**: Reduce instances during off-hours
3. **Cache responses**: Reduce API calls
4. **Use cheaper models**: GPT-3.5 instead of GPT-4
5. **Monitor spending**: Set billing alerts

## Rollback Strategy

```bash
# Docker rollback
docker run -p 8000:8000 winnipeg-agent:v1.0.0

# Heroku rollback
heroku releases:rollback v10

# AWS CodeDeploy rollback
aws deploy create-deployment \
  --application-name winnipeg-agent \
  --revision-location s3://bucket/app-v1.0.0.zip
```

## Next Steps

1. Choose deployment platform
2. Set up environment variables
3. Configure monitoring
4. Set up CI/CD pipeline
5. Test in staging environment
6. Deploy to production
7. Monitor performance and costs

See [README.md](../README.md) for more information.

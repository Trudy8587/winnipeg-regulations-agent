# System Architecture

## Overview

The Winnipeg Regulations Agent is a multi-layered system designed to help the public navigate local regulations and by-laws through conversational AI.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      User Interface                          │
│  (Web UI / Chatbot / Mobile App / Slack Bot)                │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Server                             │
│  (REST API Endpoints: /search, /citations, /compliance)     │
└─────────────────┬───────────────────────────────────────────┘
                  │
         ┌────────┴────────┐
         ▼                 ▼
    ┌─────────────┐  ┌──────────────┐
    │ Regulation  │  │ Agent Core   │
    │ Agent       │  │ (LangChain)  │
    └─────────────┘  └──────────────┘
         │                 │
         └────────┬────────┘
                  ▼
    ┌─────────────────────────────────┐
    │   Tool Layer (Agent Tools)       │
    │ - search_regulations            │
    │ - create_citation               │
    │ - check_compliance              │
    └─────────────────────────────────┘
         │
         ├─────────┬─────────┬──────────┐
         ▼         ▼         ▼          ▼
    ┌────────┐ ┌────────┐ ┌─────┐  ┌────────┐
    │Vector  │ │Keyword │ │LLM  │  │Database│
    │Search  │ │Search  │ │ API │  │        │
    │(Semantic)│(BM25)   │ │(GPT4)  │Postgres│
    └────────┘ └────────┘ └─────┘  └────────┘
         │         │
         └────┬────┘
              ▼
    ┌─────────────────────────────────┐
    │    Data Layer                    │
    │                                  │
    │ - Pinecone (Vector DB)          │
    │ - PostgreSQL (Metadata)         │
    │ - JSON Files (Raw Regulations)  │
    └─────────────────────────────────┘
```

## Components

### 1. API Layer (`src/api/`)

**FastAPI Application** providing REST endpoints:

- **`/health`**: Health check
- **`/api/search`**: Main regulation search
- **`/api/citations`**: Citation generation
- **`/api/compliance`**: Compliance checking

**Features:**
- Request validation (Pydantic models)
- Error handling
- CORS support
- Logging

### 2. Agent Layer (`src/agent/`)

**RegulationAgent**: Core orchestration using LangChain

**Responsibilities:**
- Orchestrate agent tools
- Call LLM (OpenAI GPT-4)
- Format responses
- Extract citations
- Categorize queries

**Tools:**
1. **search_regulations**: Retrieve relevant regulations
2. **create_citation**: Generate formatted citations
3. **check_compliance**: Check requirements for activities

### 3. Retriever Layer (`src/retrievers/`)

**HybridRegulationRetriever**: Combines multiple search methods

**Search Methods:**

1. **Semantic Search (Vector)**
   - Uses OpenAI embeddings
   - Stored in Pinecone
   - Understands meaning and intent
   - ~60% weight

2. **Keyword Search (BM25)**
   - Exact term matching
   - Fast for specific regulations
   - ~40% weight

3. **Hybrid Ranking**
   - Combines both methods
   - Re-ranks for relevance
   - Returns top-k results

### 4. Data Layer

#### Vector Database (Pinecone)

```
Index: winnipeg-regulations

Document Schema:
{
  "id": "WBL-2024-001",
  "title": "Business Licensing By-law",
  "section": "3.2.1",
  "text": "regulation text...",
  "category": "business",
  "embedding": [0.123, 0.456, ...]  // 1536-dim OpenAI embedding
}
```

#### Metadata Database (PostgreSQL)

```sql
regulations
├── id (PK)
├── regulation_id (WBL-2024-001)
├── title
├── section
├── text
├── category
├── effective_date
├── source_url
└── created_at

search_queries
├── id (PK)
├── query
├── category
├── timestamp
└── agent_response

citations
├── id (PK)
├── regulation_id (FK)
├── created_at
└── usage_count
```

## Data Flow

### Query Processing Flow

```
1. User Query
   "What permits do I need to open a restaurant?"
   │
   ▼
2. API Validation
   - Validate query length
   - Extract category
   │
   ▼
3. Agent Processing
   - Call LLM with query
   - LLM decides which tools to use
   │
   ▼
4. Tool Execution
   - search_regulations tool
   │
   ▼
5. Retrieval
   - Semantic search (Pinecone)
   - Keyword search (BM25)
   - Hybrid ranking
   │
   ▼
6. LLM Response Generation
   - Context: regulations found
   - Prompt: user query
   - Output: answer with citations
   │
   ▼
7. Response Formatting
   - Extract citations
   - Calculate confidence
   - Format for API response
   │
   ▼
8. Return to User
   {
     "answer": "To open a restaurant...",
     "citations": [...],
     "confidence": 0.95
   }
```

## Configuration Management

Located in `src/config/settings.py`:

```python
# API Configuration
API_HOST, API_PORT, DEBUG

# OpenAI Configuration
OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE

# Pinecone Configuration
PINECONE_API_KEY, PINECONE_ENVIRONMENT, PINECONE_INDEX_NAME

# Database Configuration
DATABASE_URL

# Agent Configuration
AGENT_NAME, AGENT_DESCRIPTION
```

All configured via `.env` file.

## Deployment Architecture

### Development
```
Local Machine
├── Python Virtual Env
├── FastAPI Dev Server
├── SQLite DB (local)
└── API Docs: localhost:8000/docs
```

### Production
```
Cloud Platform (AWS/GCP/Azure)
├── Docker Container
├── Load Balancer
├── Multiple API Instances
├── PostgreSQL RDS
├── Pinecone Cloud
└── CloudWatch/Monitoring
```

### Docker Deployment
```
docker build -f docker/Dockerfile -t winnipeg-agent .
docker run -p 8000:8000 --env-file .env winnipeg-agent
```

## Security Considerations

1. **API Keys**: Store in environment variables, never in code
2. **Rate Limiting**: Implement per IP/API key limits
3. **Authentication**: Consider API key authentication for production
4. **Validation**: Validate all user inputs
5. **Logging**: Log queries and responses (without PII)
6. **HTTPS**: Use TLS in production

## Performance Optimization

1. **Caching**: Cache frequent queries
2. **Indexing**: Optimize Pinecone index settings
3. **Embedding Batching**: Batch embed multiple documents
4. **Connection Pooling**: Reuse database connections
5. **Async Processing**: Use async/await for I/O operations

## Monitoring & Logging

**Key Metrics:**
- Query response time
- Agent success rate
- Citation accuracy
- System uptime
- API error rates

**Logging Levels:**
- INFO: Query processing, agent decisions
- WARNING: Rate limits, degraded performance
- ERROR: Failed queries, API errors
- DEBUG: Detailed agent reasoning

## Scalability

**Horizontal Scaling:**
- Deploy multiple API instances
- Use load balancer (nginx, AWS ALB)
- Shared Pinecone index
- Shared PostgreSQL database

**Vertical Scaling:**
- Increase container resources
- Optimize LLM model selection
- Cache optimization

## Future Enhancements

1. **Multi-Language Support**: French, Cree, etc.
2. **Document Upload**: Users upload their documents
3. **Real-time Updates**: Automatic regulation updates
4. **Advanced Analytics**: Usage patterns, trending queries
5. **Mobile App**: Native iOS/Android application
6. **Integration with City Systems**: Direct API connections to city databases

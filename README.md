# Winnipeg Regulations Agent

An AI-powered agent to help the public navigate **Winnipeg by-laws** and **Manitoba regulations** for their concerns including:
- Business applications & licensing
- Facility setup & permits
- Property & zoning inquiries
- Compliance & regulatory questions
- Permits and approvals process

## 🎯 Purpose

This agent serves as a **24/7 assistant** that:
1. Searches relevant regulations and by-laws
2. Anchors/cites specific regulation sections
3. Provides clear, actionable guidance
4. Helps users understand compliance requirements

## 🏗️ Project Structure

```
winnipeg-regulations-agent/
├── src/
│   ├── agent/              # Core agent logic & orchestration
│   ├── retrievers/         # Search & retrieval layer
│   ├── llm/               # LLM integration
│   ├── api/               # REST API endpoints
│   ├── utils/             # Helpers & utilities
│   └── config/            # Configuration management
├── data/
│   ├── regulations/       # Winnipeg by-laws & Manitoba regulations
│   └── embeddings/        # Pre-computed embeddings
├── tests/                 # Unit & integration tests
├── docs/                  # User guides & API documentation
├── docker/                # Docker configuration
├── scripts/               # Data loading & setup scripts
├── .github/workflows/     # CI/CD pipelines
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip package manager
- OpenAI API key (or alternative LLM)
- Pinecone account (for vector database)

### Installation

```bash
# Clone the repository
git clone https://github.com/Trudy8587/winnipeg-regulations-agent.git
cd winnipeg-regulations-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Run the Agent

```bash
# Start the API server
python -m uvicorn src.api.main:app --reload

# Query the agent
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "What permits do I need to open a restaurant in Winnipeg?"}'
```

## 📋 Use Cases

### Business Applications
- "What are the steps to get a business license?"
- "What permits do I need for a retail store?"
- "What are the health & safety requirements?"

### Facility Setup
- "Can I build a secondary suite on my property?"
- "What are the parking requirements for a commercial building?"
- "What zoning regulations apply to my lot?"

### Compliance
- "What are the noise bylaws in Winnipeg?"
- "What are the accessibility requirements?"
- "What are the signage regulations?"

## 🛠️ Tech Stack

- **Language:** Python 3.9+
- **Framework:** FastAPI
- **LLM:** OpenAI GPT-4 (via LangChain)
- **Vector DB:** Pinecone
- **Search:** Hybrid (semantic + keyword)
- **Deployment:** Docker + Cloud Platform

## 📖 API Documentation

### Endpoint: `/api/search`

**Request:**
```json
{
  "query": "What permits do I need to open a restaurant?",
  "category": "business"  // Optional: business, zoning, permits, etc.
}
```

**Response:**
```json
{
  "query": "What permits do I need to open a restaurant?",
  "answer": "To open a restaurant in Winnipeg, you need: 1) Business License, 2) Food Service License, 3) Health Inspection...",
  "citations": [
    {
      "regulation": "Winnipeg By-law 6500/1",
      "section": "3.2.1",
      "text": "Every person operating a restaurant shall obtain a business license..."
    }
  ],
  "confidence": 0.95,
  "source_urls": ["https://winnipeg.ca/..."]
}
```

## 🔄 Data Pipeline

1. **Scrape/Download** regulations from official sources
2. **Parse** into structured format (JSON)
3. **Chunk** documents for optimal retrieval
4. **Embed** using OpenAI embeddings
5. **Index** in Pinecone vector database
6. **Deploy** and serve via API

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test
pytest tests/test_agent.py
```

## 📦 Deployment

### Docker
```bash
docker build -f docker/Dockerfile -t winnipeg-agent .
docker run -p 8000:8000 --env-file .env winnipeg-agent
```

### Cloud Deployment
- AWS ECS / Lambda
- Google Cloud Run
- Azure Container Instances

## 📝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/add-new-regulation`)
3. Commit changes (`git commit -m 'Add new regulation data'`)
4. Push to branch (`git push origin feature/add-new-regulation`)
5. Open a Pull Request

## 📄 License

MIT License - see LICENSE file for details

## 🤝 Support

For issues, questions, or feature requests, please [open an issue](https://github.com/Trudy8587/winnipeg-regulations-agent/issues).

## 📚 Resources

- [Winnipeg City Website](https://winnipeg.ca)
- [Manitoba Justice](https://gov.mb.ca/justice)
- [LangChain Documentation](https://python.langchain.com/)
- [OpenAI API](https://platform.openai.com/)

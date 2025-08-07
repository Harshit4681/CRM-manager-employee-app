# HackRx 6.0 Document Retrieval System

An LLM-powered document retrieval and analysis system that processes PDF, DOCX, and email documents to provide intelligent responses to natural language queries.

## 🚀 Features

- **Multi-format Document Processing**: PDF, DOCX, TXT, and Email support
- **Semantic Search**: Pinecone/FAISS vector database with OpenAI embeddings
- **Natural Language Query Processing**: Intent classification and entity extraction
- **LLM-Powered Analysis**: GPT-4 integration for document analysis and decision making
- **Explainable AI**: Detailed reasoning and evidence for all decisions
- **High Performance**: Optimized for <3s response times
- **Scalable Architecture**: Docker containerization with microservices design

## 📋 Requirements

- Python 3.11+
- OpenAI API Key (GPT-4 access)
- Pinecone API Key
- Docker & Docker Compose (for deployment)

## 🛠️ Quick Setup

### 1. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
OPENAI_API_KEY=your-openai-api-key-here
PINECONE_API_KEY=your-pinecone-api-key-here
```

### 2. Docker Deployment (Recommended)

```bash
# Build and start all services
docker-compose up -d

# Check service health
docker-compose ps

# View logs
docker-compose logs -f app
```

### 3. Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 🔧 API Documentation

### Main Endpoint

**POST** `/api/v1/hackrx/run`

Process documents and answer queries with structured decisions.

#### Request
```json
{
  "query": "46M, knee surgery, Pune, 3-month policy",
  "document_urls": [
    "https://example.com/policy1.pdf",
    "https://example.com/policy2.docx"
  ]
}
```

#### Response
```json
{
  "query": "46M, knee surgery, Pune, 3-month policy",
  "decisions": [
    {
      "decision_id": "dec_123",
      "document_id": "doc_abc_def",
      "document_name": "health_policy.pdf",
      "decision": "eligible",
      "reasoning": {
        "relevant_clauses": [
          "Section 4.2: Knee surgery coverage is included...",
          "Age group 40-50 eligible for full benefits..."
        ],
        "evidence": [
          "Patient age 46 falls within covered age range",
          "Knee surgery explicitly listed in covered procedures"
        ],
        "confidence_score": 0.92,
        "reasoning_steps": [
          "Step 1: Analyzed age eligibility criteria",
          "Step 2: Verified procedure coverage",
          "Step 3: Checked regional policy terms"
        ]
      },
      "key_factors": [
        "age_eligibility",
        "procedure_coverage",
        "regional_coverage"
      ],
      "recommendations": [
        "Proceed with claim submission",
        "Ensure all medical reports are attached"
      ]
    }
  ],
  "processing_time": 2.34,
  "documents_processed": 2,
  "timestamp": "2024-01-15T10:30:45Z"
}
```

### Authentication

All endpoints require Bearer token authentication:

```bash
curl -H "Authorization: Bearer your-token-here" \
     -H "Content-Type: application/json" \
     -X POST http://localhost:8000/api/v1/hackrx/run \
     -d '{"query": "test query", "document_urls": ["http://example.com/doc.pdf"]}'
```

### Additional Endpoints

- **GET** `/health` - Health check
- **POST** `/api/v1/documents/upload` - Upload single document
- **GET** `/api/v1/documents/{document_id}` - Get document info
- **POST** `/api/v1/search` - Search documents

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Document      │    │   Vector Store  │    │   LLM Service   │
│   Processor     │────│   (Pinecone/    │────│   (GPT-4)       │
│   (PDF/DOCX)    │    │    FAISS)       │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  │
                    ┌─────────────────┐
                    │   FastAPI       │
                    │   Main App      │
                    └─────────────────┘
                              │
                    ┌─────────────────┐
                    │   Query         │
                    │   Processor     │
                    └─────────────────┘
```

## 🎯 Query Examples

### Insurance Claim Validation
```
"46M, knee surgery, Pune, 3-month policy"
```

### Coverage Check
```
"What is covered for a 35-year-old female in Mumbai with diabetes?"
```

### Policy Search
```
"Find health insurance policies with maternity benefits"
```

### Premium Calculation
```
"Calculate premium for 28-year-old male in Bangalore"
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for GPT-4 | ✅ |
| `PINECONE_API_KEY` | Pinecone API key | ✅ |
| `BEARER_TOKEN` | API authentication token | ❌ |
| `DEBUG` | Enable debug mode | ❌ |
| `CHUNK_SIZE` | Document chunk size | ❌ |
| `SIMILARITY_THRESHOLD` | Vector search threshold | ❌ |

### Performance Tuning

```env
# Optimize for speed
CHUNK_SIZE=800
CHUNK_OVERLAP=150
VECTOR_SEARCH_TOP_K=8
OPENAI_MAX_TOKENS=1500

# Optimize for accuracy
CHUNK_SIZE=1200
CHUNK_OVERLAP=300
VECTOR_SEARCH_TOP_K=15
SIMILARITY_THRESHOLD=0.8
```

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=app tests/

# Test specific endpoint
curl -X POST "http://localhost:8000/api/v1/hackrx/run" \
     -H "Authorization: Bearer hackrx-demo-token" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "test query",
       "document_urls": ["https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"]
     }'
```

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### Logs
```bash
# Container logs
docker-compose logs -f app

# Application logs
tail -f logs/app.log
```

### Metrics
- Processing time per request
- Documents processed
- Vector store statistics
- LLM token usage

## 🚀 Deployment

### Production Deployment

1. **Update Environment**
   ```bash
   # Set production values
   DEBUG=false
   BEARER_TOKEN=your-secure-token
   SECRET_KEY=your-secure-secret-key
   ```

2. **Deploy with Docker**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Configure Reverse Proxy**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### Cloud Deployment

#### Heroku
```bash
# Create Heroku app
heroku create your-app-name

# Set environment variables
heroku config:set OPENAI_API_KEY=your-key
heroku config:set PINECONE_API_KEY=your-key

# Deploy
git push heroku main
```

#### AWS ECS/GCP Cloud Run
Use the provided Dockerfile for containerized deployment.

## 🔒 Security

- Bearer token authentication
- Input validation and sanitization
- Rate limiting (configurable)
- CORS configuration
- Secure headers

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏆 HackRx 6.0

This system is designed for the HackRx 6.0 competition with the following optimizations:

- **Unknown Document Handling**: 2.0x weight optimization
- **Real-time Performance**: <3s response times
- **Explainable Decisions**: Detailed reasoning and evidence
- **Modular Architecture**: Easy to extend and modify
- **Cost Optimization**: Efficient token usage and caching

### Competition Webhook

Set your webhook URL to: `https://your-deployed-app.com/api/v1/hackrx/run`

## 📞 Support

For support and questions:
- Create an issue in the repository
- Contact: your-email@example.com

---

Built with ❤️ for HackRx 6.0
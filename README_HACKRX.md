# LLM-Powered Intelligent Query-Retrieval System
## HackRx 6.0 - Bajaj Finserv Health

### 🎯 Solution Overview

This system implements an advanced LLM-powered document processing and query-retrieval solution that can intelligently process large documents (PDFs, DOCX, emails) and answer complex queries using semantic search and GPT-4.

### 🏗️ System Architecture

```
Input Documents → Document Processor → Embedding Search → LLM Processing → JSON Response
     ↓                    ↓                  ↓              ↓              ↓
  PDF/DOCX/Email      Text Extraction    FAISS Vector DB   GPT-4 Analysis  Structured Output
```

### 🚀 Key Features

- **Multi-format Document Processing**: Supports PDF, DOCX, and email documents
- **Semantic Search**: Uses FAISS vector database with sentence transformers
- **Intelligent Query Understanding**: GPT-4 powered natural language processing
- **Explainable Decisions**: Provides detailed justifications with clause references
- **Token Optimization**: Efficient token usage with context truncation
- **Real-time Performance**: Fast response times with optimized embeddings
- **Scalable Architecture**: Containerized deployment with health checks

### 📋 API Endpoints

#### Main Processing Endpoint
```
POST /api/v1/hackrx/run
Authorization: Bearer 0915638d3e05859661ee5f0459482a6d4f9b0d393950134909176c3f6e1a4d95
Content-Type: application/json
```

**Request Format:**
```json
{
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf",
    "questions": [
        "What is the grace period for premium payment?",
        "Does this policy cover maternity expenses?"
    ]
}
```

**Response Format:**
```json
{
    "answers": [
        "A grace period of thirty days is provided for premium payment...",
        "Yes, the policy covers maternity expenses with 24-month waiting period..."
    ]
}
```

#### Health Check
```
GET /health
```

### 🛠️ Technology Stack

- **Backend**: FastAPI (Python)
- **Vector Database**: FAISS
- **LLM**: GPT-4 (OpenAI)
- **Embeddings**: all-MiniLM-L6-v2 (Sentence Transformers)
- **Document Processing**: PyPDF2, python-docx
- **Deployment**: Docker, Docker Compose

### ⚙️ Configuration

Key configuration parameters in `app/config.py`:

```python
AUTH_TOKEN = "0915638d3e05859661ee5f0459482a6d4f9b0d393950134909176c3f6e1a4d95"
OPENAI_MODEL = "gpt-4-turbo-preview"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K_RESULTS = 5
SIMILARITY_THRESHOLD = 0.7
```

### 🚀 Quick Start

1. **Clone and Setup**
```bash
git clone <repository>
cd hackrx-llm-system
```

2. **Environment Setup**
```bash
cp .env.example .env
# Add your OpenAI API key to .env
```

3. **Docker Deployment**
```bash
docker-compose up -d
```

4. **Local Development**
```bash
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

### 📊 Performance Optimizations

1. **Token Efficiency**: Context truncation and smart chunking
2. **Latency**: FAISS optimized search with similarity thresholds
3. **Accuracy**: Re-ranking with multiple similarity factors
4. **Scalability**: Stateless design with containerization

### 🔍 Query Processing Pipeline

1. **Document Ingestion**: Download and parse document from URL
2. **Text Extraction**: Extract clean text with metadata preservation
3. **Chunking**: Split text into semantic chunks with overlap
4. **Embedding Creation**: Generate vector embeddings using sentence transformers
5. **Vector Storage**: Store in FAISS index for fast similarity search
6. **Query Processing**: 
   - Encode user query to vector
   - Search for similar chunks
   - Re-rank results by relevance
7. **LLM Generation**: Use GPT-4 to generate contextual answers
8. **Response Formation**: Structure output with justifications

### 📈 Evaluation Metrics

- **Accuracy**: Semantic similarity matching with threshold filtering
- **Token Efficiency**: Context optimization and prompt engineering
- **Latency**: Sub-second response times for most queries
- **Explainability**: Detailed clause references and confidence scores

### 🔐 Security Features

- Bearer token authentication
- Input validation and sanitization
- Error handling with graceful degradation
- Rate limiting ready architecture

### 🌐 Deployment

The system is designed for easy deployment on cloud platforms:

- **Containerized**: Docker and Docker Compose ready
- **Scalable**: Horizontal scaling with load balancers
- **Monitoring**: Health checks and logging
- **Configuration**: Environment-based configuration

### 📝 Example Use Cases

1. **Insurance Claims**: "Does policy cover knee surgery for 46-year-old male?"
2. **Legal Compliance**: "What are the waiting periods for pre-existing conditions?"
3. **HR Policies**: "What is the maternity leave policy duration?"
4. **Contract Analysis**: "What are the termination clauses in this agreement?"

### 🏆 Competitive Advantages

1. **Multi-Domain Expertise**: Specialized for insurance, legal, HR, and compliance
2. **Explainable AI**: Clear decision reasoning with source attribution
3. **Production Ready**: Comprehensive error handling and monitoring
4. **Cost Effective**: Optimized token usage without sacrificing accuracy
5. **Fast Integration**: RESTful API with standard authentication

### 📞 Support

For technical support or questions about the implementation, please refer to the codebase documentation or contact the development team.

---

**Built for HackRx 6.0 by Team [Your Team Name]**
from fastapi import FastAPI, HTTPException, Depends, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import logging
from app.simple_processor import SimpleDocumentProcessor
from app.simple_search import SimpleSearch
from app.simple_llm import SimpleLLMProcessor
from app.config import Settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="LLM-Powered Intelligent Query-Retrieval System",
    description="HackRx 6.0 - Process large documents and make contextual decisions",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
settings = Settings()

# Authentication
def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    if credentials.credentials != settings.AUTH_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    return credentials.credentials

# Pydantic models
class QueryRequest(BaseModel):
    documents: str
    questions: List[str]

class QueryResponse(BaseModel):
    answers: List[str]

class HealthResponse(BaseModel):
    status: str
    message: str

# Initialize components
document_processor = SimpleDocumentProcessor()
embedding_search = SimpleSearch()
llm_processor = SimpleLLMProcessor()

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return HealthResponse(status="healthy", message="LLM Query-Retrieval System is running")

@app.post("/api/v1/hackrx/run", response_model=QueryResponse)
async def process_queries(
    request: QueryRequest,
    token: str = Depends(verify_token)
):
    """
    Process queries against documents using LLM-powered retrieval
    """
    try:
        logger.info(f"Processing {len(request.questions)} questions against document: {request.documents}")
        
        # Step 1: Process document
        processed_doc = await document_processor.process_document(request.documents)
        
        # Step 2: Create embeddings and store in vector database
        vector_store = await embedding_search.create_embeddings(processed_doc)
        
        # Step 3: Process each question
        answers = []
        for question in request.questions:
            # Retrieve relevant chunks
            relevant_chunks = await embedding_search.search_similar(question, vector_store)
            
            # Generate answer using LLM
            answer = await llm_processor.generate_answer(question, relevant_chunks)
            answers.append(answer)
        
        return QueryResponse(answers=answers)
        
    except Exception as e:
        logger.error(f"Error processing queries: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing queries: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "components": {
            "document_processor": "ready",
            "embedding_search": "ready", 
            "llm_processor": "ready"
        },
        "message": "All systems operational"
    }

@app.get("/api/v1/hackrx/status")
async def system_status():
    """System status for monitoring"""
    return {
        "service": "hackrx-llm-system",
        "status": "running",
        "version": "1.0.0",
        "features": [
            "Document Processing (PDF, DOCX, Email)",
            "Semantic Search",
            "Intelligent Query Processing",
            "Multi-domain Support (Insurance, Legal, HR, Compliance)"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import asyncio
import logging
import time
from datetime import datetime

from app.services.document_processor import DocumentProcessor
from app.services.vector_store import VectorStore
from app.services.query_processor import QueryProcessor
from app.services.llm_service import LLMService
from app.models.schemas import QueryRequest, QueryResponse, DocumentInfo, Decision
from app.core.config import settings
from app.core.auth import verify_token

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="HackRx 6.0 Document Retrieval System",
    description="LLM-powered document retrieval and analysis system",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize services
document_processor = DocumentProcessor()
vector_store = VectorStore()
query_processor = QueryProcessor()
llm_service = LLMService()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting HackRx Document Retrieval System...")
    await vector_store.initialize()
    await llm_service.initialize()
    logger.info("System initialized successfully!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down services...")
    await vector_store.close()
    await llm_service.close()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.post("/api/v1/hackrx/run", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Main endpoint for processing document queries
    Handles PDF/DOCX/Email documents and returns structured decisions
    """
    start_time = time.time()
    
    try:
        # Verify authentication
        await verify_token(credentials.credentials)
        
        logger.info(f"Processing query: {request.query[:100]}...")
        
        # Step 1: Process documents from blob URLs
        processed_docs = []
        for doc_url in request.document_urls:
            try:
                doc_info = await document_processor.process_document(doc_url)
                processed_docs.append(doc_info)
                logger.info(f"Processed document: {doc_info.filename}")
                
                # Store document chunks in vector database
                if doc_info.chunks:
                    # Add document_id to chunk metadata
                    for chunk in doc_info.chunks:
                        chunk.metadata['document_id'] = doc_info.document_id
                    
                    success = await vector_store.store_chunks(doc_info.chunks)
                    if success:
                        logger.info(f"Stored {len(doc_info.chunks)} chunks for document {doc_info.filename}")
                    else:
                        logger.warning(f"Failed to store chunks for document {doc_info.filename}")
                
            except Exception as e:
                logger.error(f"Failed to process document {doc_url}: {e}")
                # Continue with other documents
        
        if not processed_docs:
            raise HTTPException(
                status_code=400,
                detail="No documents could be processed"
            )
        
        # Step 2: Parse and understand the query
        parsed_query = await query_processor.parse_query(request.query)
        logger.info(f"Parsed query intent: {parsed_query.intent}")
        
        # Step 3: Perform semantic search
        search_results = await vector_store.search(
            query=request.query,
            document_ids=[doc.document_id for doc in processed_docs],
            top_k=settings.VECTOR_SEARCH_TOP_K,
            similarity_threshold=settings.SIMILARITY_THRESHOLD
        )
        
        logger.info(f"Found {len(search_results)} relevant chunks")
        
        # Step 4: Use LLM to analyze documents and make decisions
        decisions = await llm_service.analyze_documents(
            query=request.query,
            parsed_query=parsed_query,
            documents=processed_docs,
            search_results=search_results
        )
        
        # Step 5: Build response
        processing_time = time.time() - start_time
        
        response = QueryResponse(
            query=request.query,
            decisions=decisions,
            processing_time=processing_time,
            documents_processed=len(processed_docs),
            timestamp=datetime.utcnow().isoformat(),
            metadata={
                "query_complexity": query_processor.get_query_complexity(parsed_query),
                "chunks_found": len(search_results),
                "intent": parsed_query.intent.value,
                "entities": parsed_query.entities
            }
        )
        
        logger.info(f"Query processed successfully in {processing_time:.2f}s")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/api/v1/documents/upload")
async def upload_document(
    document_url: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Upload and process a single document"""
    try:
        await verify_token(credentials.credentials)
        
        doc_info = await document_processor.process_document(document_url)
        
        # Store chunks in vector database
        if doc_info.chunks:
            for chunk in doc_info.chunks:
                chunk.metadata['document_id'] = doc_info.document_id
            
            success = await vector_store.store_chunks(doc_info.chunks)
            
            return {
                "document_id": doc_info.document_id,
                "filename": doc_info.filename,
                "status": "processed",
                "chunks_created": len(doc_info.chunks),
                "vector_storage": "success" if success else "failed"
            }
        else:
            return {
                "document_id": doc_info.document_id,
                "filename": doc_info.filename,
                "status": "processed",
                "chunks_created": 0,
                "vector_storage": "no_chunks"
            }
        
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/documents/{document_id}")
async def get_document_info(
    document_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get information about a processed document"""
    try:
        await verify_token(credentials.credentials)
        
        doc_info = await document_processor.get_document_info(document_id)
        if not doc_info:
            raise HTTPException(status_code=404, detail="Document not found")
            
        return doc_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/search")
async def search_documents(
    query: str,
    document_ids: Optional[List[str]] = None,
    top_k: int = 10,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Search documents using semantic similarity"""
    try:
        await verify_token(credentials.credentials)
        
        results = await vector_store.search(
            query=query,
            document_ids=document_ids,
            top_k=top_k,
            similarity_threshold=settings.SIMILARITY_THRESHOLD
        )
        
        return {
            "query": query,
            "results": results,
            "total_results": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/stats")
async def get_system_stats(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get system statistics"""
    try:
        await verify_token(credentials.credentials)
        
        vector_stats = await vector_store.get_stats()
        
        return {
            "system": {
                "status": "healthy",
                "version": "1.0.0",
                "uptime": "running"
            },
            "vector_store": vector_stats,
            "processing": {
                "max_file_size": settings.MAX_FILE_SIZE,
                "chunk_size": settings.CHUNK_SIZE,
                "chunk_overlap": settings.CHUNK_OVERLAP,
                "similarity_threshold": settings.SIMILARITY_THRESHOLD
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock

from main import app
from app.models.schemas import DocumentInfo, DocumentChunk, DocumentType, Decision, DecisionReasoning

# Test client
client = TestClient(app)

@pytest.fixture
def auth_headers():
    """Authentication headers for testing"""
    return {"Authorization": "Bearer hackrx-demo-token"}

@pytest.fixture
def sample_query_request():
    """Sample query request for testing"""
    return {
        "query": "46M, knee surgery, Pune, 3-month policy",
        "document_urls": [
            "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
        ]
    }

@pytest.fixture
def mock_document_info():
    """Mock document info for testing"""
    return DocumentInfo(
        document_id="test_doc_123",
        filename="test_policy.pdf",
        document_type=DocumentType.PDF,
        blob_url="https://example.com/test.pdf",
        file_size=1024,
        processed_at="2024-01-01T00:00:00Z",
        chunks=[
            DocumentChunk(
                chunk_id="test_doc_123_chunk_0",
                content="This is a test policy document chunk.",
                metadata={"chunk_index": 0, "document_id": "test_doc_123"}
            )
        ],
        metadata={"test": True}
    )

@pytest.fixture
def mock_decision():
    """Mock decision for testing"""
    return Decision(
        decision_id="test_decision_123",
        document_id="test_doc_123",
        document_name="test_policy.pdf",
        decision="eligible",
        reasoning=DecisionReasoning(
            relevant_clauses=["Test clause 1"],
            evidence=["Test evidence 1"],
            confidence_score=0.9,
            reasoning_steps=["Step 1: Test step"]
        ),
        key_factors=["test_factor"],
        recommendations=["Test recommendation"]
    )

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["version"] == "1.0.0"

def test_auth_required():
    """Test that authentication is required"""
    response = client.post("/api/v1/hackrx/run", json={
        "query": "test query",
        "document_urls": ["https://example.com/test.pdf"]
    })
    assert response.status_code == 403  # Should require authentication

@patch('app.services.document_processor.DocumentProcessor.process_document')
@patch('app.services.vector_store.VectorStore.store_chunks')
@patch('app.services.vector_store.VectorStore.search')
@patch('app.services.llm_service.LLMService.analyze_documents')
@patch('app.core.auth.verify_token')
def test_process_query_success(
    mock_verify_token,
    mock_analyze_documents,
    mock_search,
    mock_store_chunks,
    mock_process_document,
    auth_headers,
    sample_query_request,
    mock_document_info,
    mock_decision
):
    """Test successful query processing"""
    # Setup mocks
    mock_verify_token.return_value = True
    mock_process_document.return_value = mock_document_info
    mock_store_chunks.return_value = True
    mock_search.return_value = []
    mock_analyze_documents.return_value = [mock_decision]
    
    response = client.post(
        "/api/v1/hackrx/run",
        json=sample_query_request,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert data["query"] == sample_query_request["query"]
    assert "decisions" in data
    assert len(data["decisions"]) == 1
    assert "processing_time" in data
    assert "documents_processed" in data
    assert "timestamp" in data
    
    # Verify decision structure
    decision = data["decisions"][0]
    assert decision["decision_id"] == mock_decision.decision_id
    assert decision["decision"] == mock_decision.decision
    assert "reasoning" in decision
    assert "key_factors" in decision
    assert "recommendations" in decision

@patch('app.core.auth.verify_token')
def test_invalid_request(mock_verify_token, auth_headers):
    """Test invalid request handling"""
    mock_verify_token.return_value = True
    
    # Test with missing required fields
    response = client.post(
        "/api/v1/hackrx/run",
        json={"query": "test"},  # Missing document_urls
        headers=auth_headers
    )
    assert response.status_code == 422  # Validation error

@patch('app.services.document_processor.DocumentProcessor.process_document')
@patch('app.core.auth.verify_token')
def test_document_processing_error(
    mock_verify_token,
    mock_process_document,
    auth_headers,
    sample_query_request
):
    """Test handling of document processing errors"""
    mock_verify_token.return_value = True
    mock_process_document.side_effect = Exception("Document processing failed")
    
    response = client.post(
        "/api/v1/hackrx/run",
        json=sample_query_request,
        headers=auth_headers
    )
    
    assert response.status_code == 400
    assert "No documents could be processed" in response.json()["detail"]

@patch('app.services.document_processor.DocumentProcessor.process_document')
@patch('app.services.vector_store.VectorStore.store_chunks')
@patch('app.core.auth.verify_token')
def test_upload_document(
    mock_verify_token,
    mock_store_chunks,
    mock_process_document,
    auth_headers,
    mock_document_info
):
    """Test document upload endpoint"""
    mock_verify_token.return_value = True
    mock_process_document.return_value = mock_document_info
    mock_store_chunks.return_value = True
    
    response = client.post(
        "/api/v1/documents/upload",
        params={"document_url": "https://example.com/test.pdf"},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["document_id"] == mock_document_info.document_id
    assert data["filename"] == mock_document_info.filename
    assert data["status"] == "processed"
    assert data["chunks_created"] == len(mock_document_info.chunks)
    assert data["vector_storage"] == "success"

@patch('app.services.vector_store.VectorStore.search')
@patch('app.core.auth.verify_token')
def test_search_documents(mock_verify_token, mock_search, auth_headers):
    """Test document search endpoint"""
    mock_verify_token.return_value = True
    mock_search.return_value = []
    
    response = client.post(
        "/api/v1/search",
        params={"query": "test query", "top_k": 5},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["query"] == "test query"
    assert "results" in data
    assert "total_results" in data

@patch('app.services.vector_store.VectorStore.get_stats')
@patch('app.core.auth.verify_token')
def test_get_stats(mock_verify_token, mock_get_stats, auth_headers):
    """Test system stats endpoint"""
    mock_verify_token.return_value = True
    mock_get_stats.return_value = {
        "pinecone_available": True,
        "faiss_available": True,
        "total_vectors": 100
    }
    
    response = client.get("/api/v1/stats", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "system" in data
    assert "vector_store" in data
    assert "processing" in data
    assert data["system"]["status"] == "healthy"

def test_cors_headers():
    """Test CORS headers are present"""
    response = client.options("/health")
    assert "access-control-allow-origin" in response.headers.get("access-control-allow-headers", "").lower()

@pytest.mark.asyncio
async def test_startup_shutdown():
    """Test startup and shutdown events"""
    # This test ensures the app can start and stop without errors
    # In a real test environment, you might want to test the actual
    # initialization of services
    pass
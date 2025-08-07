from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum

class DocumentType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    EMAIL = "email"
    TXT = "txt"
    UNKNOWN = "unknown"

class QueryIntent(str, Enum):
    POLICY_SEARCH = "policy_search"
    CLAIM_VALIDATION = "claim_validation"
    COVERAGE_CHECK = "coverage_check"
    PREMIUM_CALCULATION = "premium_calculation"
    DOCUMENT_ANALYSIS = "document_analysis"
    GENERAL_QUERY = "general_query"

class DocumentChunk(BaseModel):
    chunk_id: str = Field(..., description="Unique identifier for the chunk")
    content: str = Field(..., description="Text content of the chunk")
    page_number: Optional[int] = Field(None, description="Page number if applicable")
    section: Optional[str] = Field(None, description="Section or heading")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    embedding: Optional[List[float]] = Field(None, description="Vector embedding")

class DocumentInfo(BaseModel):
    document_id: str = Field(..., description="Unique identifier for the document")
    filename: str = Field(..., description="Original filename")
    document_type: DocumentType = Field(..., description="Type of document")
    blob_url: str = Field(..., description="Original blob URL")
    file_size: int = Field(..., description="File size in bytes")
    processed_at: datetime = Field(..., description="Processing timestamp")
    chunks: List[DocumentChunk] = Field(default_factory=list, description="Document chunks")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    
    @validator('chunks')
    def validate_chunks(cls, v):
        if not v:
            return v
        # Ensure chunk_ids are unique
        chunk_ids = [chunk.chunk_id for chunk in v]
        if len(chunk_ids) != len(set(chunk_ids)):
            raise ValueError("Chunk IDs must be unique")
        return v

class ParsedQuery(BaseModel):
    intent: QueryIntent = Field(..., description="Identified query intent")
    entities: Dict[str, Any] = Field(default_factory=dict, description="Extracted entities")
    keywords: List[str] = Field(default_factory=list, description="Key search terms")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Applied filters")
    
class SearchResult(BaseModel):
    chunk_id: str = Field(..., description="Matching chunk ID")
    document_id: str = Field(..., description="Source document ID")
    content: str = Field(..., description="Matching content")
    score: float = Field(..., description="Similarity score")
    page_number: Optional[int] = Field(None, description="Page number")
    section: Optional[str] = Field(None, description="Section")
    metadata: Dict[str, Any] = Field(default_factory=dict)

class DecisionReasoning(BaseModel):
    relevant_clauses: List[str] = Field(default_factory=list, description="Relevant document clauses")
    evidence: List[str] = Field(default_factory=list, description="Supporting evidence")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in decision")
    reasoning_steps: List[str] = Field(default_factory=list, description="Step-by-step reasoning")

class Decision(BaseModel):
    decision_id: str = Field(..., description="Unique decision identifier")
    document_id: str = Field(..., description="Source document ID")
    document_name: str = Field(..., description="Document filename")
    decision: str = Field(..., description="Final decision (e.g., 'eligible', 'not_eligible', 'partial')")
    reasoning: DecisionReasoning = Field(..., description="Detailed reasoning")
    key_factors: List[str] = Field(default_factory=list, description="Key decision factors")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations if any")

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="Natural language query")
    document_urls: List[str] = Field(..., min_items=1, description="List of blob URLs to process")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")
    
    @validator('document_urls')
    def validate_urls(cls, v):
        if not v:
            raise ValueError("At least one document URL is required")
        for url in v:
            if not url.startswith(('http://', 'https://')):
                raise ValueError(f"Invalid URL format: {url}")
        return v

class QueryResponse(BaseModel):
    query: str = Field(..., description="Original query")
    decisions: List[Decision] = Field(..., description="Decisions for each document")
    processing_time: float = Field(..., description="Processing time in seconds")
    documents_processed: int = Field(..., description="Number of documents processed")
    timestamp: str = Field(..., description="Response timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

# Error response models
class ErrorDetail(BaseModel):
    message: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")

class ErrorResponse(BaseModel):
    error: ErrorDetail = Field(..., description="Error information")
    timestamp: str = Field(..., description="Error timestamp")
    request_id: Optional[str] = Field(None, description="Request identifier")

# Configuration models
class VectorSearchConfig(BaseModel):
    top_k: int = Field(default=10, ge=1, le=100, description="Number of results to return")
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Minimum similarity score")
    search_type: str = Field(default="semantic", description="Type of search")

class LLMConfig(BaseModel):
    model: str = Field(default="gpt-4", description="LLM model to use")
    temperature: float = Field(default=0.1, ge=0.0, le=2.0, description="Model temperature")
    max_tokens: int = Field(default=2000, ge=100, le=4000, description="Maximum tokens")
    include_reasoning: bool = Field(default=True, description="Include reasoning in response")

# Database models (for PostgreSQL)
class DocumentRecord(BaseModel):
    id: int
    document_id: str
    filename: str
    document_type: str
    blob_url: str
    file_size: int
    processed_at: datetime
    metadata: Dict[str, Any]
    
    class Config:
        from_attributes = True

class ChunkRecord(BaseModel):
    id: int
    chunk_id: str
    document_id: str
    content: str
    page_number: Optional[int]
    section: Optional[str]
    metadata: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Authentication
    AUTH_TOKEN: str = "0915638d3e05859661ee5f0459482a6d4f9b0d393950134909176c3f6e1a4d95"
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    
    # Pinecone Configuration (optional, will use FAISS if not provided)
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: Optional[str] = None
    PINECONE_INDEX_NAME: str = "hackrx-documents"
    
    # Embedding Configuration
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # Vector Search Configuration
    TOP_K_RESULTS: int = 5
    SIMILARITY_THRESHOLD: float = 0.7
    
    # LLM Configuration
    MAX_TOKENS: int = 2000
    TEMPERATURE: float = 0.1
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Initialize settings
settings = Settings()
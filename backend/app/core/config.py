from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "HackRx Document Retrieval System"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_PREFIX: str = "/api/v1"
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    
    # Security
    SECRET_KEY: str = "hackrx-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # Authentication
    BEARER_TOKEN: Optional[str] = None
    API_KEYS: List[str] = []
    
    # OpenAI/LLM Settings
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_TEMPERATURE: float = 0.1
    OPENAI_MAX_TOKENS: int = 2000
    EMBEDDING_MODEL: str = "text-embedding-ada-002"
    
    # Pinecone Settings
    PINECONE_API_KEY: str
    PINECONE_ENVIRONMENT: str = "gcp-starter"
    PINECONE_INDEX_NAME: str = "hackrx-documents"
    PINECONE_DIMENSION: int = 1536
    
    # Database Settings
    DATABASE_URL: str = "postgresql://user:password@localhost/hackrx"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Redis Settings (for caching)
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 3600  # 1 hour
    
    # Document Processing
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    SUPPORTED_FORMATS: List[str] = ["pdf", "docx", "txt", "eml"]
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # Vector Search
    VECTOR_SEARCH_TOP_K: int = 10
    SIMILARITY_THRESHOLD: float = 0.7
    
    # Processing Limits
    MAX_DOCUMENTS_PER_REQUEST: int = 10
    MAX_QUERY_LENGTH: int = 1000
    PROCESSING_TIMEOUT: int = 300  # 5 minutes
    
    # Monitoring
    LOG_LEVEL: str = "INFO"
    SENTRY_DSN: Optional[str] = None
    
    # Development
    RELOAD: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Validate required settings
def validate_settings():
    """Validate that all required settings are provided"""
    required_settings = [
        "OPENAI_API_KEY",
        "PINECONE_API_KEY",
    ]
    
    missing = []
    for setting in required_settings:
        if not getattr(settings, setting):
            missing.append(setting)
    
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

# Log configuration (can be imported and used)
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "formatter": "detailed",
            "class": "logging.FileHandler",
            "filename": "app.log",
        },
    },
    "root": {
        "level": settings.LOG_LEVEL,
        "handlers": ["default"],
    },
    "loggers": {
        "uvicorn": {
            "level": "INFO",
            "handlers": ["default"],
            "propagate": False,
        },
        "fastapi": {
            "level": "INFO",
            "handlers": ["default"],
            "propagate": False,
        },
    },
}
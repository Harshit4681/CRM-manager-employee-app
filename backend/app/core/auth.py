import logging
from typing import Optional
from fastapi import HTTPException, status
from jose import JWTError, jwt
from datetime import datetime, timedelta

from app.core.config import settings

logger = logging.getLogger(__name__)

async def verify_token(token: str) -> bool:
    """
    Verify Bearer token
    
    For HackRx, this can be a simple token validation
    In production, you'd integrate with proper OAuth/JWT validation
    """
    try:
        # Simple token validation for demo/competition
        if settings.BEARER_TOKEN and token == settings.BEARER_TOKEN:
            return True
        
        # Check against list of valid API keys
        if token in settings.API_KEYS:
            return True
        
        # For development/testing, allow a default token
        if settings.DEBUG and token == "hackrx-demo-token":
            return True
        
        # JWT token validation (if using JWT)
        if token.startswith("eyJ"):  # JWT tokens start with this
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
                # Add additional validation logic here
                exp = payload.get("exp")
                if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token has expired"
                    )
                return True
            except JWTError:
                pass
        
        # If no validation passes, reject
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication verification failed"
        )

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt

def validate_api_key(api_key: str) -> bool:
    """Validate API key"""
    return api_key in settings.API_KEYS
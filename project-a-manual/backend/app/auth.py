import secrets

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from .config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def require_api_key(provided: str | None = Security(api_key_header)) -> str:
    if provided is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key...pass it in the X-API-Key header.",
        )
    if not secrets.compare_digest(provided, settings.api_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key...",
        )
    return provided

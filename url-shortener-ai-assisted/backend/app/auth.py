"""API-key authentication.

Creating, listing, and inspecting URLs requires a shared secret sent in the
``X-API-Key`` header. Public redirects do not use this dependency.
"""
import secrets

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from .config import Settings, get_settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(
    provided_key: str | None = Security(api_key_header),
    settings: Settings = Depends(get_settings),
) -> None:
    # secrets.compare_digest avoids leaking timing information about the key.
    if not provided_key or not secrets.compare_digest(
        provided_key, settings.api_key
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
        )

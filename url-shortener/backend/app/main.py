"""FastAPI application: create, redirect, stats, and list endpoints."""
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .auth import require_api_key
from .config import Settings, get_settings
from .database import Base, engine, get_db

# Create tables on startup. For a larger app this would be an Alembic migration.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="URL Shortener API",
    version="1.0.0",
    description=(
        "Create short links, redirect visitors, and track click counts. "
        "Creating and inspecting links requires an API key; redirects are public."
    ),
)

_settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=_settings.cors_origin_list,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _to_response(url: models.URL, settings: Settings) -> schemas.URLResponse:
    """Attach the fully-qualified short URL to a model instance."""
    return schemas.URLResponse(
        short_code=url.short_code,
        short_url=f"{settings.base_url.rstrip('/')}/{url.short_code}",
        long_url=url.long_url,
        click_count=url.click_count,
        created_at=url.created_at,
        expires_at=url.expires_at,
    )


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/api/shorten",
    response_model=schemas.URLResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_api_key)],
    tags=["urls"],
)
def shorten_url(
    payload: schemas.URLCreate,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> schemas.URLResponse:
    """Create a short URL from a long URL. Idempotent for duplicate URLs."""
    url = crud.create_url(
        db, long_url=str(payload.long_url), expires_in_days=payload.expires_in_days
    )
    return _to_response(url, settings)


@app.get(
    "/api/urls",
    response_model=list[schemas.URLResponse],
    dependencies=[Depends(require_api_key)],
    tags=["urls"],
)
def list_all_urls(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> list[schemas.URLResponse]:
    """List every created URL, newest first (powers the dashboard)."""
    return [_to_response(u, settings) for u in crud.list_urls(db)]


@app.get(
    "/api/stats/{short_code}",
    response_model=schemas.StatsResponse,
    dependencies=[Depends(require_api_key)],
    tags=["urls"],
)
def get_stats(
    short_code: str, db: Session = Depends(get_db)
) -> schemas.StatsResponse:
    """Return click count and metadata for a single short code."""
    url = crud.get_by_code(db, short_code)
    if url is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short code not found.",
        )
    return schemas.StatsResponse(
        short_code=url.short_code,
        long_url=url.long_url,
        click_count=url.click_count,
        created_at=url.created_at,
        expires_at=url.expires_at,
        is_expired=url.is_expired,
    )


@app.get("/{short_code}", tags=["redirect"])
def redirect(short_code: str, db: Session = Depends(get_db)) -> RedirectResponse:
    """Public redirect. Resolves a code and forwards to the original URL."""
    url = crud.get_by_code(db, short_code)
    if url is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short code not found.",
        )
    if url.is_expired:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="This short link has expired.",
        )
    crud.increment_clicks(db, short_code)
    # 307 preserves the method; a browser GET follows it to the target.
    return RedirectResponse(
        url=url.long_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT
    )

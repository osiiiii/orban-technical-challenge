"""Data-access helpers. Keeps DB logic out of the route handlers."""
import secrets
import string
from datetime import timedelta

from sqlalchemy import update
from sqlalchemy.orm import Session

from . import models
from .config import get_settings
from .models import _utcnow

# URL-safe base62 alphabet (no look-alike padding characters).
_ALPHABET = string.ascii_letters + string.digits


def generate_short_code(db: Session, length: int) -> str:
    """Generate a random base62 code that is not already taken.

    Random (rather than sequential) codes avoid making the ID space
    enumerable. Collisions are astronomically unlikely at length 6, but we
    retry a few times to be safe, then widen the code as a last resort.
    """
    for _ in range(10):
        code = "".join(secrets.choice(_ALPHABET) for _ in range(length))
        exists = (
            db.query(models.URL.id)
            .filter(models.URL.short_code == code)
            .first()
        )
        if not exists:
            return code
    # Extremely unlikely fallback: widen the code space.
    return generate_short_code(db, length + 1)


def get_by_code(db: Session, short_code: str) -> models.URL | None:
    return (
        db.query(models.URL)
        .filter(models.URL.short_code == short_code)
        .first()
    )


def get_active_by_long_url(db: Session, long_url: str) -> models.URL | None:
    """Return an existing, non-expired mapping for this long URL, if any."""
    candidates = (
        db.query(models.URL)
        .filter(models.URL.long_url == long_url)
        .all()
    )
    for url in candidates:
        if not url.is_expired:
            return url
    return None


def create_url(
    db: Session, long_url: str, expires_in_days: int | None
) -> models.URL:
    """Create a new short URL.

    Duplicate handling: if the same long URL already has an active mapping,
    return it instead of minting a new code. This keeps the table clean and
    makes shortening idempotent for repeated submissions.
    """
    existing = get_active_by_long_url(db, long_url)
    if existing is not None:
        return existing

    settings = get_settings()
    code = generate_short_code(db, settings.code_length)
    expires_at = (
        _utcnow() + timedelta(days=expires_in_days)
        if expires_in_days
        else None
    )
    url = models.URL(
        short_code=code,
        long_url=long_url,
        expires_at=expires_at,
    )
    db.add(url)
    db.commit()
    db.refresh(url)
    return url


def increment_clicks(db: Session, short_code: str) -> None:
    """Atomically bump the click counter for a code."""
    db.execute(
        update(models.URL)
        .where(models.URL.short_code == short_code)
        .values(click_count=models.URL.click_count + 1)
    )
    db.commit()


def list_urls(db: Session) -> list[models.URL]:
    return (
        db.query(models.URL)
        .order_by(models.URL.created_at.desc())
        .all()
    )

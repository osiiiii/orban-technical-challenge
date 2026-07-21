"""Database models."""
from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class URL(Base):
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # The generated short code, e.g. "abc123". Unique + indexed for fast lookup.
    short_code: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )

    # The original long URL. Indexed so we can detect duplicates quickly.
    long_url: Mapped[str] = mapped_column(String, index=True, nullable=False)

    click_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    # Optional expiry. NULL means the link never expires.
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        expires = self.expires_at
        # SQLite may return a naive datetime; treat it as UTC.
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        return _utcnow() >= expires

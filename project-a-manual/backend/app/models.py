from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    body: Mapped[str] = mapped_column(Text, nullable=False, default="")
    tags: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utcnow,
        onupdate=_utcnow,
        server_default=func.now(),
    )

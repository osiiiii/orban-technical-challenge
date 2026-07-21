"""Pydantic schemas for request and response bodies."""
from datetime import datetime

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, field_validator


class URLCreate(BaseModel):
    # AnyHttpUrl enforces a valid http/https URL with a host. Invalid URLs
    # are rejected by FastAPI with a 422 before reaching our handler.
    long_url: AnyHttpUrl

    # Optional number of days until the link expires. Must be positive.
    expires_in_days: int | None = Field(default=None, gt=0, le=3650)

    @field_validator("long_url")
    @classmethod
    def _stringify(cls, v: AnyHttpUrl) -> str:
        # Store/return the URL as a plain string rather than a Url object.
        return str(v)


class URLResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    short_code: str
    short_url: str
    long_url: str
    click_count: int
    created_at: datetime
    expires_at: datetime | None


class StatsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    short_code: str
    long_url: str
    click_count: int
    created_at: datetime
    expires_at: datetime | None
    is_expired: bool

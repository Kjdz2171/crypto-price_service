"""Pydantic schemas for API request/response validation."""

from pydantic import BaseModel, ConfigDict


class PriceBase(BaseModel):
    """Shared fields for price payloads."""
    ticker: str
    price: float
    timestamp: int


class PriceRead(PriceBase):
    """Price record as returned by list/by-date endpoints."""
    id: int
    model_config = ConfigDict(from_attributes=True)


class LatestPriceResponse(BaseModel):
    """Single latest price (no id)."""
    ticker: str
    price: float
    timestamp: int


class HealthResponse(BaseModel):
    """Health check payload."""
    status: str

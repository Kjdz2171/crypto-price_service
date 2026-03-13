from pydantic import BaseModel


class PriceBase(BaseModel):
    ticker: str
    price: float
    timestamp: int


class PriceRead(PriceBase):
    id: int

    class Config:
        from_attributes = True


class LatestPriceResponse(BaseModel):
    ticker: str
    price: float
    timestamp: int


class HealthResponse(BaseModel):
    status: str


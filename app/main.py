"""FastAPI application: HTTP API for stored Deribit index prices."""

from typing import Annotated, AsyncIterator, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from .config import get_settings
from .database import create_engine_and_session_factory, init_db
from .repositories import PriceRepository
from .schemas import HealthResponse, LatestPriceResponse, PriceRead
from .services import PriceService


async def get_db(request: Request) -> AsyncIterator[AsyncSession]:
    """Yield a DB session from the app-state session factory."""
    async with request.app.state.session_factory() as session:
        yield session


def get_price_service(db: Annotated[AsyncSession, Depends(get_db)]) -> PriceService:
    """Build PriceService with repository bound to the request session."""
    return PriceService(PriceRepository(db))


app = FastAPI(
    title=get_settings().app_name,
    description="REST API for historical BTC/ETH index prices from Deribit.",
)

DBSessionDep = Annotated[AsyncSession, Depends(get_db)]
PriceServiceDep = Annotated[PriceService, Depends(get_price_service)]


@app.on_event("startup")
async def on_startup() -> None:
    """Create DB engine, session factory, and tables on first run."""
    settings = get_settings()
    engine, session_factory = create_engine_and_session_factory(settings)
    app.state.engine = engine
    app.state.session_factory = session_factory
    await init_db(engine)


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check() -> HealthResponse:
    """Liveness probe."""
    return HealthResponse(status="ok")


@app.get(
    "/prices",
    response_model=list[PriceRead],
    tags=["prices"],
    summary="List all prices for a ticker",
)
async def list_prices(
    ticker: Annotated[str, Query(description="Ticker, e.g. btc_usd or eth_usd")],
    price_service: PriceServiceDep,
    start_ts: Annotated[
        Optional[int],
        Query(description="Start of range (UNIX ms, inclusive)"),
    ] = None,
    end_ts: Annotated[
        Optional[int],
        Query(description="End of range (UNIX ms, inclusive)"),
    ] = None,
) -> list[PriceRead]:
    """Return all stored prices for the given ticker, optionally filtered by time range."""
    prices = await price_service.get_all_by_ticker(
        ticker, start_ts=start_ts, end_ts=end_ts
    )
    return [PriceRead.model_validate(p) for p in prices]


@app.get(
    "/prices/latest",
    response_model=LatestPriceResponse,
    tags=["prices"],
    summary="Get latest price for a ticker",
)
async def latest_price(
    ticker: Annotated[str, Query(description="Ticker, e.g. btc_usd or eth_usd")],
    price_service: PriceServiceDep,
) -> LatestPriceResponse:
    """Return the most recent stored price for the given ticker. 404 if none."""
    price = await price_service.get_latest(ticker)
    if price is None:
        raise HTTPException(
            status_code=404,
            detail="No price data for this ticker",
        )
    return LatestPriceResponse(
        ticker=price.ticker,
        price=price.price,
        timestamp=price.timestamp,
    )


@app.get(
    "/prices/by-date",
    response_model=list[PriceRead],
    tags=["prices"],
    summary="Get prices for a ticker filtered by date range",
)
async def prices_by_date(
    ticker: Annotated[str, Query(description="Ticker, e.g. btc_usd or eth_usd")],
    price_service: PriceServiceDep,
    start_ts: Annotated[
        Optional[int],
        Query(description="Start of range (UNIX ms, inclusive)"),
    ] = None,
    end_ts: Annotated[
        Optional[int],
        Query(description="End of range (UNIX ms, inclusive)"),
    ] = None,
) -> list[PriceRead]:
    """Return stored prices for the ticker within the given timestamp range."""
    prices = await price_service.get_all_by_ticker(
        ticker, start_ts=start_ts, end_ts=end_ts
    )
    return [PriceRead.model_validate(p) for p in prices]

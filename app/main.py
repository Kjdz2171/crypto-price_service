from typing import Annotated, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from .config import get_settings
from .database import create_engine_and_session_factory, init_db
from .schemas import HealthResponse, LatestPriceResponse, PriceRead


async def get_db(request: Request) -> AsyncSession:
    """Yield a DB session from app-state factory. No module-level engine."""
    async with request.app.state.session_factory() as session:
        yield session


app = FastAPI(
    title=get_settings().app_name,
)

DBSessionDep = Annotated[AsyncSession, Depends(get_db)]


@app.on_event("startup")
async def on_startup() -> None:
    settings = get_settings()
    engine, session_factory = create_engine_and_session_factory(settings)
    app.state.engine = engine
    app.state.session_factory = session_factory
    await init_db(engine)


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check() -> HealthResponse:
    return HealthResponse(status="ok")


from .repositories import PriceRepository
from .services import PriceService


def get_price_service(db: DBSessionDep) -> PriceService:
    """Build PriceService from session (DI)."""
    return PriceService(PriceRepository(db))


PriceServiceDep = Annotated[PriceService, Depends(get_price_service)]


@app.get(
    "/prices",
    response_model=list[PriceRead],
    tags=["prices"],
)
async def list_prices(
    ticker: Annotated[str, Query(description="Ticker (e.g. btc_usd, eth_usd)")],
    price_service: PriceServiceDep,
    start_ts: Annotated[
        Optional[int],
        Query(description="Start UNIX timestamp in ms (inclusive)"),
    ] = None,
    end_ts: Annotated[
        Optional[int],
        Query(description="End UNIX timestamp in ms (inclusive)"),
    ] = None,
) -> list[PriceRead]:
    """
    Get all stored prices for a given ticker.

    Optional `start_ts` and `end_ts` allow filtering by timestamp range.
    """
    prices = await price_service.get_all_by_ticker(
        ticker, start_ts=start_ts, end_ts=end_ts
    )
    return [PriceRead.model_validate(p) for p in prices]


@app.get(
    "/prices/latest",
    response_model=LatestPriceResponse,
    tags=["prices"],
)
async def latest_price(
    ticker: Annotated[str, Query(description="Ticker (e.g. btc_usd, eth_usd)")],
    price_service: PriceServiceDep,
) -> LatestPriceResponse:
    """Get the latest stored price for a given ticker."""
    price = await price_service.get_latest(ticker)
    if price is None:
        raise HTTPException(
            status_code=404, detail="No price data for this ticker"
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
)
async def prices_by_date(
    ticker: Annotated[str, Query(description="Ticker (e.g. btc_usd, eth_usd)")],
    price_service: PriceServiceDep,
    start_ts: Annotated[
        Optional[int],
        Query(description="Start UNIX timestamp in ms (inclusive)"),
    ] = None,
    end_ts: Annotated[
        Optional[int],
        Query(description="End UNIX timestamp in ms (inclusive)"),
    ] = None,
) -> list[PriceRead]:
    """Get stored prices for a given ticker filtered by date range."""
    prices = await price_service.get_all_by_ticker(
        ticker, start_ts=start_ts, end_ts=end_ts
    )
    return [PriceRead.model_validate(p) for p in prices]

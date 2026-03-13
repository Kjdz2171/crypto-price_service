from collections.abc import Sequence
from typing import Optional

from sqlalchemy import Select, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Price


async def get_prices_by_ticker(
    db: AsyncSession,
    ticker: str,
    start_ts: Optional[int] = None,
    end_ts: Optional[int] = None,
) -> Sequence[Price]:
    stmt: Select = select(Price).where(Price.ticker == ticker)

    if start_ts is not None:
        stmt = stmt.where(Price.timestamp >= start_ts)
    if end_ts is not None:
        stmt = stmt.where(Price.timestamp <= end_ts)

    stmt = stmt.order_by(Price.timestamp.asc())
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_latest_price(
    db: AsyncSession,
    ticker: str,
) -> Optional[Price]:
    stmt: Select = (
        select(Price)
        .where(Price.ticker == ticker)
        .order_by(desc(Price.timestamp))
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.scalars().first()


async def create_price(
    db: AsyncSession,
    *,
    ticker: str,
    price: float,
    timestamp: int,
) -> Price:
    db_obj = Price(ticker=ticker, price=price, timestamp=timestamp)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


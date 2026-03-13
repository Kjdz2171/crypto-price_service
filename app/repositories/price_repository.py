"""Data access for Price records (repository pattern)."""

from collections.abc import Sequence
from typing import Optional

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Price


class PriceRepository:
    """DB operations for the prices table."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_all_by_ticker(
        self,
        ticker: str,
        start_ts: Optional[int] = None,
        end_ts: Optional[int] = None,
    ) -> Sequence[Price]:
        """Return prices for ticker, optionally in [start_ts, end_ts] (UNIX ms)."""
        stmt = select(Price).where(Price.ticker == ticker)
        if start_ts is not None:
            stmt = stmt.where(Price.timestamp >= start_ts)
        if end_ts is not None:
            stmt = stmt.where(Price.timestamp <= end_ts)
        stmt = stmt.order_by(Price.timestamp.asc())
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def find_latest_by_ticker(self, ticker: str) -> Optional[Price]:
        """Return the latest price for ticker, or None."""
        stmt = (
            select(Price)
            .where(Price.ticker == ticker)
            .order_by(desc(Price.timestamp))
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def add(self, ticker: str, price: float, timestamp: int) -> Price:
        """Insert a price row and return it."""
        record = Price(ticker=ticker, price=price, timestamp=timestamp)
        self._session.add(record)
        await self._session.commit()
        await self._session.refresh(record)
        return record

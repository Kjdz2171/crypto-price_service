"""Application service for price queries (delegates to repository)."""

from collections.abc import Sequence
from typing import Optional

from ..models import Price
from ..repositories import PriceRepository


class PriceService:
    """Read operations for stored prices."""

    def __init__(self, repository: PriceRepository) -> None:
        self._repo = repository

    async def get_all_by_ticker(
        self,
        ticker: str,
        start_ts: Optional[int] = None,
        end_ts: Optional[int] = None,
    ) -> Sequence[Price]:
        """Return all prices for ticker, optionally filtered by time range (UNIX ms)."""
        return await self._repo.find_all_by_ticker(
            ticker, start_ts=start_ts, end_ts=end_ts
        )

    async def get_latest(self, ticker: str) -> Optional[Price]:
        """Return the latest price for ticker, or None."""
        return await self._repo.find_latest_by_ticker(ticker)

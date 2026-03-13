"""Deribit public API client for index prices (aiohttp)."""

import asyncio
import time
from typing import Any

import aiohttp

from .config import get_settings


class DeribitClientError(Exception):
    """Raised when Deribit API returns an error or unexpected format."""
    pass


class DeribitClient:
    """HTTP client for Deribit public endpoints (e.g. index price)."""

    def __init__(self, base_url: str | None = None) -> None:
        self._base_url = (base_url or get_settings().deribit_base_url).rstrip("/")

    async def _request(
        self,
        session: aiohttp.ClientSession,
        path: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        url = f"{self._base_url}{path}"
        async with session.get(url, params=params, timeout=10) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise DeribitClientError(f"Deribit API error {resp.status}: {text}")
            data = await resp.json()
            if "result" not in data:
                raise DeribitClientError(f"Unexpected response: {data}")
            return data["result"]

    async def get_index_price(self, index_name: str) -> tuple[float, int]:
        """Fetch index price for index_name. Returns (price, timestamp_ms)."""
        async with aiohttp.ClientSession() as session:
            result = await self._request(
                session,
                "/public/get_index_price",
                {"index_name": index_name},
            )
        price = float(result["index_price"])
        timestamp_ms = int(time.time() * 1000)
        return price, timestamp_ms


async def fetch_prices_for_indices(
    indices: list[str],
) -> dict[str, tuple[float, int]]:
    """Fetch index prices for all given indices concurrently."""
    client = DeribitClient()

    async def fetch_one(name: str) -> tuple[str, float, int]:
        price, ts = await client.get_index_price(name)
        return name, price, ts

    tasks = [fetch_one(idx) for idx in indices]
    results = await asyncio.gather(*tasks)
    return {name: (price, ts) for name, price, ts in results}

import asyncio
import time
from typing import Any

import aiohttp

from .config import get_settings


class DeribitClientError(Exception):
    pass


class DeribitClient:
    """HTTP client for Deribit public API (index prices)."""

    def __init__(self, base_url: str | None = None) -> None:
        self._base_url = base_url or get_settings().deribit_base_url

    async def _request(
        self,
        session: aiohttp.ClientSession,
        path: str,
        params: dict[str, Any],
    ) -> Any:
        url = f"{self._base_url}{path}"
        async with session.get(url, params=params, timeout=10) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise DeribitClientError(f"Deribit API error {resp.status}: {text}")
            data = await resp.json()
            if "result" not in data:
                raise DeribitClientError(f"Unexpected response format: {data}")
            return data["result"]

    async def get_index_price(self, index_name: str) -> tuple[float, int]:
        """Return (price, timestamp_ms) for a given Deribit index."""
        async with aiohttp.ClientSession() as session:
            result = await self._request(
                session,
                "/public/get_index_price",
                {"index_name": index_name},
            )
        price = float(result["index_price"])
        # Deribit result may not contain its own timestamp; use local UNIX time in ms.
        timestamp_ms = int(time.time() * 1000)
        return price, timestamp_ms


async def fetch_prices_for_indices(indices: list[str]) -> dict[str, tuple[float, int]]:
    """Convenience helper to fetch multiple indices concurrently."""
    client = DeribitClient()

    async def fetch_one(name: str) -> tuple[str, float, int]:
        price, ts = await client.get_index_price(name)
        return name, price, ts

    tasks = [asyncio.create_task(fetch_one(idx)) for idx in indices]
    results = await asyncio.gather(*tasks)
    return {name: (price, ts) for name, price, ts in results}


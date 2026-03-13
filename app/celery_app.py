"""Celery app and periodic task: fetch Deribit index prices every minute."""

import asyncio
from datetime import timedelta
from typing import TYPE_CHECKING

from celery import Celery

from .config import get_settings
from .database import create_engine_and_session_factory
from .deribit_client import fetch_prices_for_indices
from .repositories import PriceRepository

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

_settings = get_settings()
celery_app = Celery(
    "crypto_price_service",
    broker=_settings.celery_broker_url,
    backend=_settings.celery_result_backend,
)
celery_app.conf.beat_schedule = {
    "fetch-deribit-prices-every-minute": {
        "task": "app.celery_app.fetch_and_store_prices",
        "schedule": timedelta(minutes=1),
    },
}
celery_app.conf.timezone = "UTC"

_worker_session_factory: "async_sessionmaker[AsyncSession] | None" = None


def _get_worker_session_factory() -> "async_sessionmaker[AsyncSession]":
    """Lazy-init session factory for the worker process (one per process)."""
    global _worker_session_factory
    if _worker_session_factory is None:
        _, _worker_session_factory = create_engine_and_session_factory(
            get_settings()
        )
    return _worker_session_factory


async def _fetch_and_store() -> None:
    """Fetch btc_usd and eth_usd index prices from Deribit and persist to DB."""
    settings = get_settings()
    indices = list(settings.tracked_indices)
    prices = await fetch_prices_for_indices(indices)

    session_factory = _get_worker_session_factory()
    async with session_factory() as session:
        repo = PriceRepository(session)
        for index_name, (price, timestamp) in prices.items():
            await repo.add(index_name, price, timestamp)


@celery_app.task(name="app.celery_app.fetch_and_store_prices")
def fetch_and_store_prices() -> None:
    """Celery task entry: run async fetch-and-store in a new event loop."""
    asyncio.run(_fetch_and_store())

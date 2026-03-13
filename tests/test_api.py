"""API tests: health, list prices, latest price."""

import asyncio
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import create_engine_and_session_factory, init_db
from app.main import app
from app.models import Price


@pytest.fixture(scope="session")
def _engine_and_factory():
    """Create DB engine and session factory once per session; create tables."""
    settings = get_settings()
    engine, session_factory = create_engine_and_session_factory(settings)
    asyncio.run(init_db(engine))
    return engine, session_factory


@pytest.fixture
async def db_session(_engine_and_factory) -> AsyncSession:
    """Provide a DB session for tests."""
    _, session_factory = _engine_and_factory
    async with session_factory() as session:
        yield session


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


async def test_latest_price_not_found(client: TestClient) -> None:
    response = client.get("/prices/latest", params={"ticker": "non_existing"})
    assert response.status_code == 404


async def test_create_and_get_latest_price(
    db_session: AsyncSession,
    client: TestClient,
) -> None:
    price = Price(
        ticker="btc_usd",
        price=50000.0,
        timestamp=int(datetime.utcnow().timestamp() * 1000),
    )
    db_session.add(price)
    await db_session.commit()

    response = client.get("/prices/latest", params={"ticker": "btc_usd"})
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "btc_usd"
    assert data["price"] == 50000.0

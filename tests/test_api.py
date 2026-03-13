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
    """Create DB engine and session factory once per test session; init tables."""
    settings = get_settings()
    engine, session_factory = create_engine_and_session_factory(settings)
    asyncio.run(init_db(engine))
    return engine, session_factory


@pytest.fixture
async def db_session(_engine_and_factory) -> AsyncSession:
    """Provide a DB session for tests (no global engine)."""
    _, session_factory = _engine_and_factory
    async with session_factory() as session:
        yield session


@pytest.fixture
def client():
    return TestClient(app)


@pytest.mark.asyncio
async def test_latest_price_not_found(client: TestClient) -> None:
    response = client.get("/prices/latest", params={"ticker": "non_existing"})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_and_get_latest_price(
    db_session: AsyncSession,
    client: TestClient,
) -> None:
    # Arrange: insert a price directly
    price = Price(
        ticker="btc_usd",
        price=50000.0,
        timestamp=int(datetime.utcnow().timestamp() * 1000),
    )
    db_session.add(price)
    await db_session.commit()

    # Act
    response = client.get("/prices/latest", params={"ticker": "btc_usd"})

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "btc_usd"
    assert data["price"] == 50000.0

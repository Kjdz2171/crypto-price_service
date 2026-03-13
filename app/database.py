from collections.abc import AsyncIterator
from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

if TYPE_CHECKING:
    from .config import Settings


class Base(DeclarativeBase):
    pass


def create_engine_and_session_factory(
    settings: "Settings",
) -> tuple[AsyncEngine, async_sessionmaker]:
    """Create engine and session factory from settings. No module-level globals."""
    engine: AsyncEngine = create_async_engine(
        settings.database_url_async,
        echo=False,
        future=True,
    )
    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )
    return engine, session_factory


async def init_db(engine: AsyncEngine) -> None:
    """Create database tables if they do not exist."""
    from . import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

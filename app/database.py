"""Database engine and session factory. No module-level engine/session globals."""

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
    """SQLAlchemy declarative base for all models."""
    pass


def create_engine_and_session_factory(
    settings: "Settings",
) -> tuple[AsyncEngine, async_sessionmaker]:
    """Build async engine and session factory from settings."""
    engine = create_async_engine(
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
    """Create tables if they do not exist."""
    from . import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

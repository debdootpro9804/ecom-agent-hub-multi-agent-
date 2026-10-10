# src/ecom_hub/db/session.py
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from ecom_hub.config import DATABASE_URL

# One engine for the whole app. It manages a pool of connections.
# pool_pre_ping checks a connection is alive before using it.
engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

# A factory that creates sessions. expire_on_commit=False keeps objects
# readable after commit, which async code needs.
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Open a session, commit if everything worked, roll back if anything failed.
    Used by agent tools and scripts.
    """
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: gives each request its own session."""
    async with get_session() as session:
        yield session
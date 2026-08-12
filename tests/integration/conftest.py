from collections.abc import AsyncGenerator

import pytest
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings
from app.db.models import MonitoredService


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a clean asynchronous database session for a test."""
    engine = create_async_engine(
        settings.database_url,
        echo=False,
    )

    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        try:
            # Clean database before the test.
            await session.execute(
                delete(MonitoredService)
            )
            await session.commit()

            yield session

        finally:
            # Clean database after the test.
            await session.execute(
                delete(MonitoredService)
            )
            await session.commit()

    await engine.dispose()
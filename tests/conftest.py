from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.security import create_access_token
from app.db.models import CircuitState, MonitoredService
from app.main import app
from app.services.health_checker import HealthChecker


@pytest.fixture
def service() -> MonitoredService:
    """Create a monitored service for testing."""
    now = datetime.now(timezone.utc)

    return MonitoredService(
        id=1,
        name="test-service",
        url="https://example.com",
        timeout=5,
        failure_threshold=3,
        recovery_timeout=30,
        state=CircuitState.CLOSED,
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def repository() -> MagicMock:
    """Create a mocked service repository."""
    repository = MagicMock()
    repository.update = AsyncMock()

    return repository


@pytest.fixture
def checker(repository: MagicMock) -> HealthChecker:
    """Create a HealthChecker with a mocked repository."""
    return HealthChecker(repository)


@pytest.fixture
async def client() -> AsyncClient:
    """Create an asynchronous HTTP client for the FastAPI application."""
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        yield client


@pytest.fixture
def access_token() -> str:
    """Create a default access token for testing."""
    return create_access_token("test-user")


@pytest.fixture
def user_token() -> str:
    """Create an access token for a regular user."""
    return create_access_token(
        "test-user",
        role="user",
    )


@pytest.fixture
def admin_token() -> str:
    """Create an access token for an administrator."""
    return create_access_token(
        "test-admin",
        role="admin",
    )


def pytest_configure(config) -> None:
    """Register custom pytest markers used by the test suite."""
    config.addinivalue_line(
        "markers",
        "unit: unit tests",
    )
    config.addinivalue_line(
        "markers",
        "integration: integration tests",
    )
    config.addinivalue_line(
        "markers",
        "slow: slow tests",
    )
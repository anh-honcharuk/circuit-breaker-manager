import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import CircuitState, MonitoredService
from app.db.repositories.service import ServiceRepository


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_and_get_service(
    db_session: AsyncSession,
) -> None:
    """Create a service and retrieve it by its ID."""
    repository = ServiceRepository(db_session)

    service = MonitoredService(
        name="integration-test-service",
        url="https://example.com",
        timeout=5,
        failure_threshold=3,
        recovery_timeout=30,
        state=CircuitState.CLOSED,
    )

    created = await repository.create(service)

    assert created.id is not None
    assert created.name == "integration-test-service"

    found = await repository.get_by_id(created.id)

    assert found is not None
    assert found.id == created.id
    assert found.name == "integration-test-service"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_by_name(
    db_session: AsyncSession,
) -> None:
    """Retrieve a monitored service by its name."""
    repository = ServiceRepository(db_session)

    service = MonitoredService(
        name="find-by-name-service",
        url="https://example.com",
        timeout=5,
        failure_threshold=3,
        recovery_timeout=30,
        state=CircuitState.CLOSED,
    )

    await repository.create(service)

    found = await repository.get_by_name(
        "find-by-name-service"
    )

    assert found is not None
    assert found.name == "find-by-name-service"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_by_id_returns_none_for_missing_service(
    db_session: AsyncSession,
) -> None:
    """Return None when a service with the given ID does not exist."""
    repository = ServiceRepository(db_session)

    result = await repository.get_by_id(999999)

    assert result is None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_all(
    db_session: AsyncSession,
) -> None:
    """Return all monitored services stored in the database."""
    repository = ServiceRepository(db_session)

    service = MonitoredService(
        name="get-all-service",
        url="https://example.com",
        timeout=5,
        failure_threshold=3,
        recovery_timeout=30,
        state=CircuitState.CLOSED,
    )

    await repository.create(service)

    services = await repository.get_all()

    assert len(services) >= 1
    assert any(
        item.name == "get-all-service"
        for item in services
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_update_service(
    db_session: AsyncSession,
) -> None:
    """Update an existing service and verify the persisted changes."""
    repository = ServiceRepository(db_session)

    service = MonitoredService(
        name="update-service",
        url="https://example.com",
        timeout=5,
        failure_threshold=3,
        recovery_timeout=30,
        state=CircuitState.CLOSED,
    )

    await repository.create(service)

    service.state = CircuitState.OPEN

    updated = await repository.update(service)

    assert updated.state == CircuitState.OPEN

    found = await repository.get_by_id(service.id)

    assert found is not None
    assert found.state == CircuitState.OPEN
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.db.models import CircuitState, MonitoredService


@pytest.mark.asyncio
async def test_protected_endpoint_without_token(
    client: AsyncClient,
) -> None:
    """Reject requests without an authentication token."""
    response = await client.post(
        "/circuit-breaker/1/trip",
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_protected_endpoint_with_invalid_token(
    client: AsyncClient,
) -> None:
    """Reject requests with an invalid authentication token."""
    response = await client.post(
        "/circuit-breaker/1/trip",
        headers={
            "Authorization": "Bearer invalid-token",
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_user_cannot_trip_circuit_breaker(
    client: AsyncClient,
    user_token: str,
) -> None:
    """Prevent regular users from manually tripping a circuit breaker."""
    response = await client.post(
        "/circuit-breaker/1/trip",
        headers={
            "Authorization": f"Bearer {user_token}",
        },
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_trip_circuit_breaker(
    client: AsyncClient,
    admin_token: str,
) -> None:
    """Allow an administrator to manually open a circuit breaker."""
    service = MonitoredService(
        id=1,
        name="test-service",
        url="https://example.com",
        timeout=5,
        failure_threshold=3,
        recovery_timeout=30,
        state=CircuitState.CLOSED,
    )

    repository = AsyncMock()
    repository.get_by_id.return_value = service
    repository.update.return_value = service

    with patch(
        "app.api.routes.circuit_breaker.ServiceRepository",
        return_value=repository,
    ):
        response = await client.post(
            "/circuit-breaker/1/trip",
            headers={
                "Authorization": f"Bearer {admin_token}",
            },
        )

    assert response.status_code == 200
    assert service.state == CircuitState.OPEN

    repository.get_by_id.assert_awaited_once_with(1)
    repository.update.assert_awaited_once_with(service)


@pytest.mark.asyncio
async def test_admin_cannot_trip_nonexistent_service(
    client: AsyncClient,
    admin_token: str,
) -> None:
    """Return 404 when an administrator tries to trip a nonexistent service."""
    repository = AsyncMock()
    repository.get_by_id.return_value = None

    with patch(
        "app.api.routes.circuit_breaker.ServiceRepository",
        return_value=repository,
    ):
        response = await client.post(
            "/circuit-breaker/999/trip",
            headers={
                "Authorization": f"Bearer {admin_token}",
            },
        )

    assert response.status_code == 404

    repository.get_by_id.assert_awaited_once_with(999)
    repository.update.assert_not_awaited()


@pytest.mark.asyncio
async def test_admin_trip_changes_state_to_open(
    client: AsyncClient,
    admin_token: str,
) -> None:
    """Change the circuit state from CLOSED to OPEN."""
    service = MonitoredService(
        id=1,
        name="test-service",
        url="https://example.com",
        timeout=5,
        failure_threshold=3,
        recovery_timeout=30,
        state=CircuitState.CLOSED,
    )

    repository = AsyncMock()
    repository.get_by_id.return_value = service
    repository.update.return_value = service

    with patch(
        "app.api.routes.circuit_breaker.ServiceRepository",
        return_value=repository,
    ):
        response = await client.post(
            "/circuit-breaker/1/trip",
            headers={
                "Authorization": f"Bearer {admin_token}",
            },
        )

    assert response.status_code == 200
    assert service.state == CircuitState.OPEN
    assert repository.update.await_count == 1


@pytest.mark.asyncio
async def test_admin_can_trip_already_open_circuit(
    client: AsyncClient,
    admin_token: str,
) -> None:
    """Handle a request to trip a circuit that is already open."""
    service = MonitoredService(
        id=1,
        name="test-service",
        url="https://example.com",
        timeout=5,
        failure_threshold=3,
        recovery_timeout=30,
        state=CircuitState.OPEN,
    )

    repository = AsyncMock()
    repository.get_by_id.return_value = service
    repository.update.return_value = service

    with patch(
        "app.api.routes.circuit_breaker.ServiceRepository",
        return_value=repository,
    ):
        response = await client.post(
            "/circuit-breaker/1/trip",
            headers={
                "Authorization": f"Bearer {admin_token}",
            },
        )

    assert response.status_code == 200
    assert service.state == CircuitState.OPEN

    repository.get_by_id.assert_awaited_once_with(1)
    repository.update.assert_awaited_once_with(service)


@pytest.mark.asyncio
async def test_admin_trip_returns_expected_response(
    client: AsyncClient,
    admin_token: str,
) -> None:
    """Return the expected response after successfully tripping a circuit."""
    service = MonitoredService(
        id=1,
        name="test-service",
        url="https://example.com",
        timeout=5,
        failure_threshold=3,
        recovery_timeout=30,
        state=CircuitState.CLOSED,
    )

    repository = AsyncMock()
    repository.get_by_id.return_value = service
    repository.update.return_value = service

    with patch(
        "app.api.routes.circuit_breaker.ServiceRepository",
        return_value=repository,
    ):
        response = await client.post(
            "/circuit-breaker/1/trip",
            headers={
                "Authorization": f"Bearer {admin_token}",
            },
        )

    assert response.status_code == 200
    assert response.json()["state"] == CircuitState.OPEN
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from app.db.models import CircuitState, MonitoredService


@pytest.mark.asyncio
async def test_get_health(
    client: AsyncClient,
    service: MonitoredService,
) -> None:
    """Return the current health status of an existing service."""
    repository = AsyncMock()
    repository.get_by_id.return_value = service

    health_result = MagicMock()
    health_result.status = "healthy"
    health_result.state = CircuitState.CLOSED
    health_result.response_time_ms = 100.0

    health_checker = AsyncMock()
    health_checker.check_health.return_value = health_result

    with (
        patch(
            "app.api.routes.health.ServiceRepository",
            return_value=repository,
        ),
        patch(
            "app.api.routes.health.HealthChecker",
            return_value=health_checker,
        ),
    ):
        response = await client.get("/health/1")

    assert response.status_code == 200

    data = response.json()

    assert data["service_id"] == 1
    assert data["service_name"] == "test-service"
    assert data["status"] == "healthy"
    assert data["state"] == "CLOSED"
    assert data["response_time_ms"] == 100.0

    repository.get_by_id.assert_awaited_once_with(1)
    health_checker.check_health.assert_awaited_once_with(service)


@pytest.mark.asyncio
async def test_get_health_service_not_found(
    client: AsyncClient,
) -> None:
    """Return 404 when the requested service does not exist."""
    repository = AsyncMock()
    repository.get_by_id.return_value = None

    with patch(
        "app.api.routes.health.ServiceRepository",
        return_value=repository,
    ):
        response = await client.get("/health/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Service not found"

    repository.get_by_id.assert_awaited_once_with(999999)
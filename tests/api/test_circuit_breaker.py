from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.db.models import MonitoredService


@pytest.mark.asyncio
async def test_trip_circuit_breaker(
    client: AsyncClient,
    service: MonitoredService,
    admin_token: str,
) -> None:
    """Open the circuit breaker for an existing service."""
    repository = AsyncMock()
    repository.get_by_id.return_value = service
    repository.update.return_value = None

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
    assert response.json()["service_id"] == 1
    assert response.json()["state"] == "OPEN"

    repository.get_by_id.assert_awaited_once_with(1)
    repository.update.assert_awaited_once()


@pytest.mark.asyncio
async def test_trip_circuit_breaker_service_not_found(
    client: AsyncClient,
    admin_token: str,
) -> None:
    """Return 404 when the requested service does not exist."""
    repository = AsyncMock()
    repository.get_by_id.return_value = None

    with patch(
        "app.api.routes.circuit_breaker.ServiceRepository",
        return_value=repository,
    ):
        response = await client.post(
            "/circuit-breaker/999999/trip",
            headers={
                "Authorization": f"Bearer {admin_token}",
            },
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Service not found"

    repository.get_by_id.assert_awaited_once_with(999999)
    repository.update.assert_not_awaited()
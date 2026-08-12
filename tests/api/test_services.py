from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.db.models import MonitoredService


@pytest.mark.asyncio
async def test_register_service(
    client: AsyncClient,
    admin_token: str,
    service: MonitoredService,
) -> None:
    """Register a new monitored service as an administrator."""
    repository = AsyncMock()

    service_service = AsyncMock()
    service_service.register_service.return_value = service

    with (
        patch(
            "app.api.routes.services.ServiceRepository",
            return_value=repository,
        ),
        patch(
            "app.api.routes.services.ServiceService",
            return_value=service_service,
        ),
    ):
        response = await client.post(
            "/register-service",
            headers={
                "Authorization": f"Bearer {admin_token}",
            },
            json={
                "name": "test-service",
                "url": "https://example.com",
                "timeout": 5,
                "failure_threshold": 3,
                "recovery_timeout": 30,
            },
        )

    assert response.status_code == 201
    assert response.json()["name"] == "test-service"

    service_service.register_service.assert_awaited_once()
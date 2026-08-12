import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.db.models import CircuitState, MonitoredService
from app.services.health_checker import HealthChecker


@pytest.mark.unit
@pytest.mark.asyncio
async def test_health_check_success(
    service: MonitoredService,
    checker: HealthChecker,
) -> None:
    """Return a healthy status when the monitored service responds successfully."""
    checker.cache.get = AsyncMock(return_value=None)
    checker.cache.set = AsyncMock()

    mock_response = MagicMock()
    mock_response.is_success = True

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)

    with (
        patch(
            "app.services.health_checker.httpx.AsyncClient"
        ) as mock_async_client,
        patch(
            "app.services.health_checker.health_check_event.delay"
        ) as mock_delay,
    ):
        mock_async_client.return_value.__aenter__.return_value = mock_client

        result = await checker.check_health(service)

    assert result.status == "healthy"
    assert result.state == CircuitState.CLOSED

    mock_client.get.assert_awaited_once()
    checker.cache.set.assert_awaited_once()
    mock_delay.assert_called_once()
import time

import pytest
from httpx import AsyncClient


@pytest.mark.slow
@pytest.mark.asyncio
async def test_health_endpoint_response_time(
    client: AsyncClient,
) -> None:
    """Ensure the health endpoint responds within the expected time limit."""
    start_time = time.perf_counter()

    response = await client.get("/health/1")

    response_time = time.perf_counter() - start_time

    assert response.status_code in (200, 404)
    assert response_time < 2.0


@pytest.mark.slow
@pytest.mark.asyncio
async def test_metrics_response_time(
    client: AsyncClient,
) -> None:
    """Ensure the metrics endpoint responds within the expected time limit."""
    start_time = time.perf_counter()

    response = await client.get("/metrics")

    response_time = time.perf_counter() - start_time

    assert response.status_code == 200
    assert response_time < 2.0
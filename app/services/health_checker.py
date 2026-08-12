import time
from dataclasses import dataclass

import httpx
import structlog

from app.core.metrics import (
    circuit_breaker_state,
    health_check_duration,
    health_checks_total,
)
from app.db.models import CircuitState, MonitoredService
from app.db.repositories.service import ServiceRepository
from app.services.circuit_breaker import CircuitBreaker
from app.services.health_cache import HealthCache
from app.workers.tasks import health_check_event


logger = structlog.get_logger()


@dataclass
class HealthCheckResult:
    """Result of an external service health check."""

    status: str
    state: CircuitState
    response_time_ms: float | None


class HealthChecker:
    """Performs health checks for monitored external services.

    Uses Redis caching, Circuit Breaker state management, PostgreSQL
    persistence, Prometheus metrics, and asynchronous event processing.
    """

    def __init__(
        self,
        repository: ServiceRepository,
    ) -> None:
        """Initialize the health checker with a service repository."""
        self.cache = HealthCache()
        self.repository = repository

    async def check_health(
        self,
        service: MonitoredService,
    ) -> HealthCheckResult:
        """Check the health of a monitored external service.

        Returns a cached result when available. Otherwise, checks whether
        the Circuit Breaker allows the request, performs an asynchronous
        HTTP request, updates the circuit state, stores the result in Redis,
        persists the service state, records metrics, and publishes a
        health-check event.
        """
        cached = await self.cache.get(service.id)

        if cached is not None:
            return HealthCheckResult(
                status=cached["status"],
                state=CircuitState(cached["state"]),
                response_time_ms=cached["response_time_ms"],
            )

        circuit_breaker = CircuitBreaker(service)

        if not circuit_breaker.can_execute():
            result = HealthCheckResult(
                status="unhealthy",
                state=circuit_breaker.state,
                response_time_ms=None,
            )

            await self.cache.set(
                service.id,
                {
                    "status": result.status,
                    "state": result.state.value,
                    "response_time_ms": result.response_time_ms,
                },
            )

            return result

        start_time = time.perf_counter()

        try:
            async with httpx.AsyncClient(
                timeout=service.timeout,
            ) as client:
                response = await client.get(service.url)

            response_time_ms = (
                time.perf_counter() - start_time
            ) * 1000

            if response.is_success:
                circuit_breaker.record_success()
                await self.repository.update(service)

                result = HealthCheckResult(
                    status="healthy",
                    state=circuit_breaker.state,
                    response_time_ms=response_time_ms,
                )
            else:
                circuit_breaker.record_failure()
                await self.repository.update(service)

                result = HealthCheckResult(
                    status="unhealthy",
                    state=circuit_breaker.state,
                    response_time_ms=response_time_ms,
                )

        except (
            httpx.TimeoutException,
            httpx.ConnectError,
            httpx.RequestError,
        ):
            circuit_breaker.record_failure()
            await self.repository.update(service)

            result = HealthCheckResult(
                status="unhealthy",
                state=circuit_breaker.state,
                response_time_ms=None,
            )

        await self.cache.set(
            service.id,
            {
                "status": result.status,
                "state": result.state.value,
                "response_time_ms": result.response_time_ms,
            },
        )

        health_checks_total.labels(
            service_id=str(service.id),
            status=result.status,
        ).inc()

        health_check_duration.labels(
            service_id=str(service.id),
        ).observe(
            (result.response_time_ms or 0) / 1000
        )

        circuit_breaker_state.labels(
            service_id=str(service.id),
        ).set(
            {
                "CLOSED": 0,
                "HALF_OPEN": 1,
                "OPEN": 2,
            }[result.state.value]
        )

        logger.info(
            "health_check_completed",
            service_id=service.id,
            service_name=service.name,
            status=result.status,
            state=result.state.value,
            response_time_ms=result.response_time_ms,
        )

        health_check_event.delay(
            service.id,
            result.status,
        )

        return result
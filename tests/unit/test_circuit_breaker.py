import pytest

from app.db.models import CircuitState, MonitoredService
from app.services.circuit_breaker import CircuitBreaker


@pytest.mark.unit
def test_initial_state_is_closed(
    service: MonitoredService,
) -> None:
    """Initialize the circuit breaker in the CLOSED state."""
    circuit_breaker = CircuitBreaker(service)

    assert circuit_breaker.state == CircuitState.CLOSED


@pytest.mark.unit
def test_trip_opens_circuit(
    service: MonitoredService,
) -> None:
    """Transition the circuit breaker to the OPEN state when tripped."""
    circuit_breaker = CircuitBreaker(service)

    circuit_breaker.trip()

    assert circuit_breaker.state == CircuitState.OPEN


@pytest.mark.unit
def test_success_closes_circuit(
    service: MonitoredService,
) -> None:
    """Close the circuit after a successful operation."""
    circuit_breaker = CircuitBreaker(service)

    circuit_breaker.trip()
    circuit_breaker.record_success()

    assert circuit_breaker.state == CircuitState.CLOSED


@pytest.mark.unit
def test_failures_open_circuit(
    service: MonitoredService,
) -> None:
    """Open the circuit when the failure threshold is reached."""
    circuit_breaker = CircuitBreaker(service)

    circuit_breaker.record_failure()
    circuit_breaker.record_failure()
    circuit_breaker.record_failure()

    assert circuit_breaker.state == CircuitState.OPEN
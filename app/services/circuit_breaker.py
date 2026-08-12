from datetime import datetime, timedelta, timezone

from app.db.models import CircuitState, MonitoredService


class CircuitBreaker:
    """Implements the Circuit Breaker pattern for a monitored service."""

    def __init__(self, service: MonitoredService) -> None:
        """Initialize the circuit breaker with the service configuration."""
        self.service = service
        self.state = service.state
        self.failure_count = 0
        self.last_failure_at: datetime | None = None

    def record_success(self) -> None:
        """Record a successful request and close the circuit."""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.service.state = CircuitState.CLOSED

    def record_failure(self) -> None:
        """Record a failed request and open the circuit if threshold is reached."""
        self.failure_count += 1
        self.last_failure_at = datetime.now(timezone.utc)

        if self.failure_count >= self.service.failure_threshold:
            self.state = CircuitState.OPEN
            self.service.state = CircuitState.OPEN

    def trip(self) -> None:
        """Manually open the circuit breaker."""
        self.state = CircuitState.OPEN
        self.service.state = CircuitState.OPEN
        self.last_failure_at = datetime.now(timezone.utc)

    def can_execute(self) -> bool:
        """Check whether a request can be executed.

        Moves the circuit from OPEN to HALF_OPEN after the recovery timeout.
        """
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            if self.last_failure_at is None:
                return False

            recovery_time = timedelta(
                seconds=self.service.recovery_timeout
            )

            if (
                datetime.now(timezone.utc) - self.last_failure_at
                >= recovery_time
            ):
                self.state = CircuitState.HALF_OPEN
                self.service.state = CircuitState.HALF_OPEN
                return True

            return False

        if self.state == CircuitState.HALF_OPEN:
            return True

        return False
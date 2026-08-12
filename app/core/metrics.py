from prometheus_client import Counter, Gauge, Histogram


health_checks_total = Counter(
    "health_checks_total",
    "Total number of health checks",
    ["service_id", "status"],
)

health_check_duration = Histogram(
    "health_check_duration_seconds",
    "Health check duration in seconds",
    ["service_id"],
)

circuit_breaker_state = Gauge(
    "circuit_breaker_state",
    "Current circuit breaker state",
    ["service_id"],
)
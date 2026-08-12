# Microservice Resilience Platform

Критично важливий мікросервіс **Circuit Breaker Manager** для моніторингу зовнішніх API та автоматичного керування їхнім станом.

## Опис

Сервіс забезпечує:

- моніторинг здоров'я зовнішніх API;
- асинхронні health checks через `httpx`;
- Circuit Breaker pattern зі станами `CLOSED`, `OPEN`, `HALF_OPEN`;
- кешування результатів у Redis;
- асинхронну обробку подій через Celery;
- зберігання конфігурації сервісів у PostgreSQL;
- Prometheus metrics;
- WebSocket для real-time статусів;
- структуроване JSON-логування;
- unit-тести з моками та інтеграційні тести.

## Технології

- Python 3.12
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL
- Alembic
- Redis
- Celery
- httpx
- Prometheus
- Structlog
- Pytest
- Docker / Docker Compose

## Локальний запуск

### 1. Запустити Docker-сервіси

У корені проєкту:

```bash
docker compose up -d
```

Перевірити статус:

```bash
docker compose ps
```

Основні контейнери:

```text
api
postgres
redis
celery_worker
```

### 2. Перевірити API

API доступний за адресою:

```text
http://127.0.0.1:8001
```

Swagger:

```text
http://127.0.0.1:8001/docs
```

### 3. Перевірити health check

```powershell
Invoke-RestMethod -Method GET -Uri "http://127.0.0.1:8001/health/1"
```

Приклад відповіді:

```json
{
  "service_id": 1,
  "service_name": "payment-api",
  "status": "healthy",
  "state": "CLOSED",
  "response_time_ms": 1626.8,
  "checked_at": "2026-08-13T06:21:04.629173Z"
}
```

## API Endpoints

### Register service

```http
POST /register-service
```

Реєструє зовнішній сервіс для моніторингу.

### Health check

```http
GET /health/{service_id}
```

Виконує перевірку зовнішнього API та повертає його поточний статус.

### Circuit Breaker

```http
POST /circuit-breaker/{service_id}/trip
```

Ручне переведення Circuit Breaker у стан `OPEN`.

### Prometheus metrics

```http
GET /metrics
```

Повертає Prometheus metrics.

Основні метрики:

```text
health_checks_total
health_check_duration_seconds
circuit_breaker_state
```

### WebSocket

```text
WS /ws/status
```

Передає поточні статуси зареєстрованих сервісів у real-time.

Підключення:

```text
ws://127.0.0.1:8001/ws/status
```

## Circuit Breaker

Сервіс використовує три стани:

```text
CLOSED
   │
   │ failures >= threshold
   ▼
 OPEN
   │
   │ recovery timeout
   ▼
HALF_OPEN
   │
   ├── success ──► CLOSED
   │
   └── failure ──► OPEN
```

### `CLOSED`

Зовнішній сервіс працює нормально. Запити дозволені.

### `OPEN`

Зовнішній сервіс вважається недоступним. Запити блокуються.

### `HALF_OPEN`

Після `recovery_timeout` виконується пробний запит для перевірки відновлення сервісу.

## Redis

Результати health checks кешуються в Redis.

Ключ має формат:

```text
health:{service_id}
```

TTL кешу:

```text
10 seconds
```

Це дозволяє не виконувати повторний HTTP-запит до зовнішнього API при кожному зверненні до `/health/{service_id}`.

## Celery

Celery використовується для асинхронної обробки health-check events.

Worker запускається як окремий Docker-контейнер:

```text
celery_worker
```

Перегляд логів:

```bash
docker compose logs -f celery_worker
```

## PostgreSQL

PostgreSQL використовується для зберігання конфігурації monitored services.

Основна модель:

```text
MonitoredService
├── id
├── name
├── url
├── timeout
├── failure_threshold
├── recovery_timeout
├── state
├── created_at
└── updated_at
```

Міграції виконуються через Alembic.

Створення нової міграції:

```bash
uv run alembic revision --autogenerate -m "description"
```

Застосування міграцій:

```bash
uv run alembic upgrade head
```

## Логування

Використовується `structlog` із JSON-форматом.

Приклад події:

```json
{
  "event": "health_check_completed",
  "service_id": 1,
  "service_name": "payment-api",
  "status": "healthy",
  "state": "CLOSED",
  "response_time_ms": 1626.8,
  "level": "info",
  "timestamp": "2026-08-13T06:21:04Z"
}
```

Основні налаштування:

```env
DEBUG=true
LOG_LEVEL=INFO
```

## Тести

Unit-тести:

```bash
uv run pytest -v
```

Тести покривають:

* Circuit Breaker state transitions;
* успішні health checks;
* невдалі health checks;
* використання Redis cache;
* HTTP-запити через mocks;
* асинхронну логіку.

## Docker

Запустити всі сервіси:

```bash
docker compose up -d
```

Переглянути статус:

```bash
docker compose ps
```

Переглянути логи API:

```bash
docker compose logs -f api
```

Переглянути логи Celery:

```bash
docker compose logs -f celery_worker
```

Зупинити сервіси:

```bash
docker compose down
```

Перезапустити після зміни коду:

```bash
docker compose up -d --build
```

## Основний workflow

```text
External API
     │
     ▼
HealthChecker
     │
     ├── Redis cache
     │
     ├── Circuit Breaker
     │
     └── PostgreSQL
             │
             ▼
        Service state
             │
       ┌─────┴─────┐
       ▼           ▼
   Prometheus   WebSocket
       │           │
       ▼           ▼
    Metrics    Real-time status


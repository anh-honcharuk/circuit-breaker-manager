from fastapi import FastAPI

from app.api.routes.circuit_breaker import router as circuit_breaker_router
from app.api.routes.health import router as health_router
from app.api.routes.metrics import router as metrics_router
from app.api.routes.services import router as services_router
from app.api.routes.websocket import router as websocket_router
from app.core.config import settings
from app.core.logging import setup_logging


setup_logging()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

app.include_router(services_router)
app.include_router(health_router)
app.include_router(circuit_breaker_router)
app.include_router(metrics_router)
app.include_router(websocket_router)
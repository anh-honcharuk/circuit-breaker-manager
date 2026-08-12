from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import CircuitState
from app.db.repositories.service import ServiceRepository
from app.core.security import require_admin
from app.schemas.circuit_breaker import CircuitBreakerResponse
from app.services.circuit_breaker import CircuitBreaker


router = APIRouter()


@router.post(
    "/circuit-breaker/{service_id}/trip",
    response_model=CircuitBreakerResponse,
)
async def trip_circuit_breaker(
    service_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: str = Depends(require_admin),
) -> CircuitBreakerResponse:
    repository = ServiceRepository(session)

    service = await repository.get_by_id(service_id)

    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found",
        )

    circuit_breaker = CircuitBreaker(service)
    circuit_breaker.trip()

    service.state = CircuitState.OPEN

    await repository.update(service)

    return CircuitBreakerResponse(
        service_id=service.id,
        state=service.state,
        changed_at=datetime.now(timezone.utc),
        message="Circuit breaker manually tripped",
    )
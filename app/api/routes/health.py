from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.repositories.service import ServiceRepository
from app.schemas.health import HealthResponse
from app.services.health_checker import HealthChecker


router = APIRouter()


@router.get(
    "/health/{service_id}",
    response_model=HealthResponse,
)
async def get_health(
    service_id: int,
    session: AsyncSession = Depends(get_db),
) -> HealthResponse:
    repository = ServiceRepository(session)

    service = await repository.get_by_id(service_id)

    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found",
        )

    health_checker = HealthChecker(repository)

    result = await health_checker.check_health(service)

    return HealthResponse(
        service_id=service.id,
        service_name=service.name,
        status=result.status,
        state=result.state,
        response_time_ms=result.response_time_ms,
        checked_at=datetime.now(timezone.utc),
    )
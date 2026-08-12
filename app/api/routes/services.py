from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.repositories.service import ServiceRepository
from app.core.security import get_current_user
from app.schemas.service import (
    RegisterServiceRequest,
    RegisterServiceResponse,
)
from app.services.service import (
    ServiceAlreadyExistsError,
    ServiceService,
)


router = APIRouter()


@router.post(
    "/register-service",
    response_model=RegisterServiceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_service(
    data: RegisterServiceRequest,
    session: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
) -> RegisterServiceResponse:

    repository = ServiceRepository(session)
    service = ServiceService(repository)

    try:
        created_service = await service.register_service(data)

    except ServiceAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return RegisterServiceResponse.model_validate(
        created_service
    )
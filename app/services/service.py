from app.db.models import MonitoredService
from app.db.repositories.service import ServiceRepository
from app.schemas.service import RegisterServiceRequest


class ServiceAlreadyExistsError(Exception):
    pass


class ServiceService:
    def __init__(
        self,
        repository: ServiceRepository,
    ) -> None:
        self.repository = repository

    async def register_service(
        self,
        data: RegisterServiceRequest,
    ) -> MonitoredService:
        existing_service = await self.repository.get_by_name(
            data.name
        )

        if existing_service is not None:
            raise ServiceAlreadyExistsError(
                f"Service '{data.name}' already exists"
            )

        service = MonitoredService(
            name=data.name,
            url=str(data.url),
            timeout=data.timeout,
            failure_threshold=data.failure_threshold,
            recovery_timeout=data.recovery_timeout,
        )

        return await self.repository.create(service)
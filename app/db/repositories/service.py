from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import MonitoredService


class ServiceRepository:
    """Provides database operations for monitored services."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository with a database session."""
        self.session = session

    async def get_by_name(
        self,
        name: str,
    ) -> MonitoredService | None:
        """Return a monitored service by its name, if it exists."""
        result = await self.session.execute(
            select(MonitoredService).where(
                MonitoredService.name == name
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id(
        self,
        service_id: int,
    ) -> MonitoredService | None:
        """Return a monitored service by its ID, if it exists."""
        result = await self.session.execute(
            select(MonitoredService).where(
                MonitoredService.id == service_id
            )
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
    ) -> list[MonitoredService]:
        """Return all monitored services."""
        result = await self.session.execute(
            select(MonitoredService)
        )

        return list(result.scalars().all())

    async def create(
        self,
        service: MonitoredService,
    ) -> MonitoredService:
        """Create and persist a new monitored service."""
        self.session.add(service)

        await self.session.commit()
        await self.session.refresh(service)

        return service

    async def update(
        self,
        service: MonitoredService,
    ) -> MonitoredService:
        """Persist changes made to an existing monitored service."""
        await self.session.commit()
        await self.session.refresh(service)

        return service
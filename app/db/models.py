import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class CircuitState(str, enum.Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class MonitoredService(Base):
    __tablename__ = "monitored_services"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    url: Mapped[str] = mapped_column(
        String(2048),
        nullable=False,
    )

    timeout: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=5.0,
    )

    failure_threshold: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=3,
    )

    recovery_timeout: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=30.0,
    )

    state: Mapped[CircuitState] = mapped_column(
        Enum(CircuitState),
        nullable=False,
        default=CircuitState.CLOSED,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
from datetime import datetime

from pydantic import AnyHttpUrl, BaseModel, Field

from app.db.models import CircuitState


class RegisterServiceRequest(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=255,
    )

    url: AnyHttpUrl

    timeout: float = Field(
        default=5.0,
        gt=0,
    )

    failure_threshold: int = Field(
        default=3,
        ge=1,
    )

    recovery_timeout: float = Field(
        default=30.0,
        gt=0,
    )


class RegisterServiceResponse(BaseModel):
    id: int
    name: str
    url: AnyHttpUrl
    timeout: float
    failure_threshold: int
    recovery_timeout: float
    state: CircuitState
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }
from datetime import datetime
from pydantic import BaseModel, field_validator
from uuid import UUID as StdUUID
from uuid6 import UUID


class BaseSchema(BaseModel):
    uuid: StdUUID
    created_at: datetime
    created_by: str | None = None
    updated_at: datetime
    updated_by: str | None = None
    deleted_at: datetime | None = None
    deleted_by: str | None = None
    is_deleted: bool = False
    version: int = 1

    model_config = {"from_attributes": True}

    @field_validator("uuid", mode="before")
    @classmethod
    def coerce_uuid(cls, v: object) -> StdUUID:
        if isinstance(v, UUID):
            return StdUUID(str(v))
        return v  # type: ignore[return-value]


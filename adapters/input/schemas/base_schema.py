from pydantic import BaseModel, field_validator
from uuid import UUID as StdUUID
from uuid6 import UUID


class BaseSchema(BaseModel):
    uuid: StdUUID

    model_config = {"from_attributes": True}

    @field_validator("uuid", mode="before")
    @classmethod
    def coerce_uuid(cls, v: object) -> StdUUID:
        if isinstance(v, UUID):
            return StdUUID(str(v))
        return v  # type: ignore[return-value]

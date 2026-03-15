from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid6 import uuid7, UUID


@dataclass
class Entity:
    uuid: UUID = field(default_factory=uuid7)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str | None = None
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_by: str | None = None
    deleted_at: datetime | None = None
    deleted_by: str | None = None
    version: int = 1

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None


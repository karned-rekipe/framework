from dataclasses import dataclass, field
from uuid6 import uuid7, UUID


@dataclass
class Entity:
    uuid: UUID = field(default_factory=uuid7)


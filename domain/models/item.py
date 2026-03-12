from dataclasses import dataclass, field
from uuid6 import uuid7, UUID
from typing import Optional


@dataclass
class Item:
    uuid: UUID = field(default_factory = uuid7)
    name: str = ""
    unit: Optional[str] = None

    def __post_init__(self) -> None:
        normalized_name = self.name.strip()
        if not normalized_name:
            raise ValueError("Item name cannot be empty")
        self.name = normalized_name

        if self.unit is not None:
            normalized_unit = self.unit.strip()
            if not normalized_unit:
                raise ValueError("Item unit cannot be empty when provided")
            self.unit = normalized_unit

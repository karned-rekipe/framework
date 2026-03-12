from dataclasses import dataclass, field
from uuid import UUID, uuid7
from typing import Optional


@dataclass
class Item:
    id: UUID = field(default_factory=uuid7)
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

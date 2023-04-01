from dataclasses import dataclass, asdict

from pyback.enum import EnumBase


class Unit(EnumBase):
    """Enumeration of Kafka modes."""

    MILLIS = 'millis'
    LAPS = 'laps'


@dataclass
class DiffLap:
    """Difference between two laps."""

    value: int
    unit: Unit

    def to_dict(self) -> dict:
        """Transform into dictionary."""
        return dict(asdict(self).items())

from enum import Enum
from typing import Any


class EnumBase(Enum):
    """Enumeration that allows comparison."""

    def __eq__(self, other: Any) -> bool:
        """Compare enumeration to other objects and strings."""
        if self.__class__ is other.__class__:
            return self.value == other.value
        elif isinstance(other, str):
            return self.value == other
        return False

    def __hash__(self) -> int:
        """Build hash of current instance."""
        return hash(self.value)


class CompetitionStatus(str, EnumBase):
    """Status of a competition."""

    PAUSED = 'paused'
    ONGOING = 'ongoing'
    FINISHED = 'finished'


class CompetitionStage(str, EnumBase):
    """Stage of a competition."""

    FREE_PRACTICE = 'free-practice'
    QUALIFYING = 'qualifying'
    RACE = 'race'


class LengthUnit(str, EnumBase):
    """Units to measure the race length."""

    LAPS = 'laps'
    MILLIS = 'millis'

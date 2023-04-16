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


class ActionType(str, EnumBase):
    """Types of actions."""

    INITIALIZE = 'initialize'
    UPDATE_COMPETITION_META = 'update-competition-meta'
    UPDATE_DRIVER = 'update-driver'
    UPDATE_TEAM = 'update-team'
    UPDATE_TIMING_ALL = 'update-timing-all'
    UPDATE_TIMING_SINGLE = 'update-timing-single'
    ADD_PIT_IN = 'add-pit-in'
    ADD_PIT_OUT = 'add-pit-out'


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


class KartStatus(str, EnumBase):
    """Status of a kart."""

    GOOD = 'good'
    BAD = 'bad'
    UNKNOWN = 'unknown'


class LengthUnit(str, EnumBase):
    """Units to measure the race length."""

    LAPS = 'laps'
    MILLIS = 'millis'


class ParserSettings(str, EnumBase):
    """All available parser settings."""

    COMPETITION_REMAINING_LENGTH = 'competition-remaining-length'
    COMPETITION_STAGE = 'competition-stage'
    TIMING_BEST_TIME = 'timing-best-time'
    TIMING_GAP = 'timing-gap'
    TIMING_INTERVAL = 'timing-interval'
    TIMING_KART_NUMBER = 'timing-kart-number'
    TIMING_LAPS = 'timing-laps'
    TIMING_LAST_LAP_TIME = 'timing-last-lap-time'
    TIMING_NAME = 'timing-name'
    TIMING_PIT_TIME = 'timing-pit-time'
    TIMING_PITS = 'timing-pits'
    TIMING_RANKING = 'timing-ranking'

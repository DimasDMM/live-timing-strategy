from ltspipe.data.base import EnumBase


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
    IGNORE_GRP = 'ignore-1'
    IGNORE_STA = 'ignore-2'
    TIMING_BEST_TIME = 'timing-best-time'
    TIMING_GAP = 'timing-gap'
    TIMING_INTERVAL = 'timing-interval'
    TIMING_KART_NUMBER = 'timing-kart-number'
    TIMING_LAP = 'timing-lap'
    TIMING_LAST_TIME = 'timing-last-time'
    TIMING_NAME = 'timing-name'
    TIMING_NUMBER_PITS = 'timing-number-pits'
    TIMING_PIT_TIME = 'timing-pit-time'
    TIMING_POSITION = 'timing-position'

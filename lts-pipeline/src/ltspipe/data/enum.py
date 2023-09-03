from ltspipe.base import EnumBase


class FlagName(str, EnumBase):
    """Name of flags."""

    WAIT_INIT = 'wait-init'


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
    TIMING_NUMBER_PITS = 'timing-number-pits'
    TIMING_PIT_TIME = 'timing-pit-time'
    TIMING_POSITION = 'timing-position'

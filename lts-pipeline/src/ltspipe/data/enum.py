from ltspipe.base import EnumBase


class ActionType(str, EnumBase):
    """Types of actions."""

    INITIALIZE = 'initialize'
    NOTIFICATION = 'notification'
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


class NotificationType(str, EnumBase):
    """Types of actions."""

    INIT_ONGOING = 'init-ongoing'
    INIT_FINISHED = 'init-finished'


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

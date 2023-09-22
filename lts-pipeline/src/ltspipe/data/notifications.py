from pydantic import Field, SerializeAsAny
from typing import Any, Dict, Optional, Type

from ltspipe.base import BaseModel, DictModel, EnumBase
from ltspipe.data.competitions import (
    CompetitionMetadata,
    Driver,
    ParticipantTiming,
    PitIn,
    PitOut,
    Team,
)
from ltspipe.data.strategy import StrategyPitsStats


class NotificationType(str, EnumBase):
    """Types of notifications."""

    DUMMY = 'dummy'  # for testing purposes
    INIT_ONGOING = 'init-ongoing'
    INIT_FINISHED = 'init-finished'
    ADDED_PIT_IN = 'added-pit-in'
    ADDED_PIT_OUT = 'added-pit-out'
    ADDED_STRATEGY_PITS_STATS = 'added-strategy-pits-stats'
    UPDATED_COMPETITION_METADATA_REMAINING = 'updated-competition-metadata-remaining'  # noqa: E501, LN001
    UPDATED_COMPETITION_METADATA_STATUS = 'updated-competition-metadata-status'
    UPDATED_DRIVER = 'updated-driver'
    UPDATED_TEAM = 'updated-team'
    UPDATED_TIMING_LAP = 'updated-timing-lap'
    UPDATED_TIMING_LAST_TIME = 'updated-timing-last-time'
    UPDATED_TIMING_NUMBER_PITS = 'updated-timing-number-pits'
    UPDATED_TIMING_PIT_TIME = 'updated-timing-pit-time'
    UPDATED_TIMING_POSITION = 'updated-timing-position'


_factory: Dict[NotificationType, Optional[Type[DictModel]]] = {
    NotificationType.DUMMY: None,
    NotificationType.INIT_ONGOING: None,
    NotificationType.INIT_FINISHED: None,
    NotificationType.ADDED_PIT_IN: PitIn,
    NotificationType.ADDED_PIT_OUT: PitOut,
    NotificationType.ADDED_STRATEGY_PITS_STATS: StrategyPitsStats,
    NotificationType.UPDATED_COMPETITION_METADATA_REMAINING: CompetitionMetadata,  # noqa: E501, LN001
    NotificationType.UPDATED_COMPETITION_METADATA_STATUS: CompetitionMetadata,
    NotificationType.UPDATED_DRIVER: Driver,
    NotificationType.UPDATED_TEAM: Team,
    NotificationType.UPDATED_TIMING_LAP: ParticipantTiming,
    NotificationType.UPDATED_TIMING_LAST_TIME: ParticipantTiming,
    NotificationType.UPDATED_TIMING_NUMBER_PITS: ParticipantTiming,
    NotificationType.UPDATED_TIMING_PIT_TIME: ParticipantTiming,
    NotificationType.UPDATED_TIMING_POSITION: ParticipantTiming,
}


class Notification(DictModel):
    """Notification data."""

    type: NotificationType
    data: Optional[SerializeAsAny[DictModel]] = Field(default=None)

    @classmethod
    def from_dict(cls, raw: dict) -> BaseModel:  # noqa: ANN102
        """Return an instance of itself with the data in the dictionary."""
        DictModel._validate_base_dict(cls, raw)  # type: ignore
        ntype = NotificationType.value_of(raw.get('type'))
        raw_data = raw.get('data')
        data = Notification.__from_dict_data(ntype, raw_data)
        return cls.model_construct(
            type=ntype,
            data=data,
        )

    @staticmethod
    def __from_dict_data(
            type: NotificationType,
            raw_data: Any) -> Any:
        """Transform the raw data into a model."""
        if type not in _factory:
            raise Exception(f'Unknown action type: {type}')
        elif _factory[type] is None:
            return raw_data

        if not isinstance(raw_data, dict):
            raise Exception(f'Unknown data format: {raw_data}')
        else:
            return _factory[type].from_dict(raw_data)  # type: ignore

from typing import Any, Dict, Type

from ltspipe.base import BaseModel, DictModel, EnumBase
from ltspipe.data.competitions import (
    AddPitIn,
    AddPitOut,
    InitialData,
    UpdateCompetitionMetadataStatus,
    UpdateDriver,
    UpdateTeam,
)


class ActionType(str, EnumBase):
    """Types of actions."""

    INITIALIZE = 'initialize'
    ADD_PIT_IN = 'add-pit-in'
    ADD_PIT_OUT = 'add-pit-out'
    UPDATE_COMPETITION_METADATA_STATUS = 'update-competition-metadata-status'
    UPDATE_DRIVER = 'update-driver'
    UPDATE_TEAM = 'update-team'
    # UPDATE_TIMING_ALL = 'update-timing-all'
    # UPDATE_TIMING_SINGLE = 'update-timing-single'


_factory: Dict[ActionType, Type[DictModel]] = {
    ActionType.INITIALIZE: InitialData,
    ActionType.ADD_PIT_IN: AddPitIn,
    ActionType.ADD_PIT_OUT: AddPitOut,
    ActionType.UPDATE_COMPETITION_METADATA_STATUS: UpdateCompetitionMetadataStatus,  # noqa: E501, LN001
    ActionType.UPDATE_DRIVER: UpdateDriver,
    ActionType.UPDATE_TEAM: UpdateTeam,
}


class Action(DictModel):
    """Apply an action to the data."""

    type: ActionType
    data: DictModel

    @classmethod
    def from_dict(cls, raw: dict) -> BaseModel:  # noqa: ANN102
        """Return an instance of itself with the data in the dictionary."""
        DictModel._validate_base_dict(cls, raw)  # type: ignore

        type = ActionType.value_of(raw.get('type'))
        raw_data = raw.get('data')
        data = Action.__from_dict_data(type, raw_data)
        return cls.construct(
            type=type,
            data=data,
        )

    @staticmethod
    def __from_dict_data(type: ActionType, raw_data: Any) -> BaseModel:
        """Transform the raw data into a model."""
        if type not in _factory or _factory[type] is None:
            raise Exception(f'Unknown action type: {type}')
        elif not isinstance(raw_data, dict):
            raise Exception(f'Unknown data format: {raw_data}')
        return _factory[type].from_dict(raw_data)

from pydantic import Field
from typing import Dict, List, Optional

from ltspipe.base import BaseModel, EnumBase
from ltspipe.data.enum import (
    LengthUnit,
    ParserSettings,
)
from ltspipe.base import DictModel


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


class Driver(DictModel):
    """Info of a driver."""

    id: int
    participant_code: str
    name: str
    team_id: Optional[int]

    @classmethod
    def from_dict(cls, raw: dict) -> BaseModel:  # noqa: ANN102
        """Return an instance of itself with the data in the dictionary."""
        DictModel._validate_base_dict(cls, raw)  # type: ignore
        return cls.construct(
            id=raw.get('id'),
            participant_code=raw.get('participant_code'),
            name=raw.get('name'),
            team_id=raw.get('team_id', None),
        )


class Team(DictModel):
    """Info of a team."""

    id: int
    participant_code: str
    name: str

    @classmethod
    def from_dict(cls, raw: dict) -> BaseModel:  # noqa: ANN102
        """Return an instance of itself with the data in the dictionary."""
        DictModel._validate_base_dict(cls, raw)  # type: ignore
        return cls.construct(
            id=raw.get('id'),
            participant_code=raw.get('participant_code'),
            name=raw.get('name'),
        )


class CompetitionInfo(BaseModel):
    """Info of a competition."""

    id: Optional[int]
    competition_code: str
    parser_settings: Dict[ParserSettings, str] = Field(default_factory=dict)
    drivers: List[Driver] = Field(default_factory=list)
    teams: List[Team] = Field(default_factory=list)


class DiffLap(DictModel):
    """Difference between two laps."""

    value: int
    unit: LengthUnit

    @classmethod
    def from_dict(cls, raw: dict) -> BaseModel:  # noqa: ANN102
        """Return an instance of itself with the data in the dictionary."""
        DictModel._validate_base_dict(cls, raw)  # type: ignore
        return cls.construct(
            value=raw.get('value'),
            unit=LengthUnit(raw.get('unit')),
        )


class Participant(DictModel):
    """Details of a participant."""

    participant_code: str
    kart_number: int
    ranking: Optional[int] = Field(default=None)
    team_name: Optional[str] = Field(default=None)
    driver_name: Optional[str] = Field(default=None)
    last_lap_time: Optional[int] = Field(default=None)
    best_time: Optional[int] = Field(default=None)
    gap: Optional[DiffLap] = Field(default=None)
    interval: Optional[DiffLap] = Field(default=None)
    laps: Optional[int] = Field(default=None)
    pits: Optional[int] = Field(default=None)
    pit_time: Optional[int] = Field(default=None)

    @classmethod
    def from_dict(cls, raw: dict) -> BaseModel:  # noqa: ANN102
        """Return an instance of itself with the data in the dictionary."""
        DictModel._validate_base_dict(cls, raw)  # type: ignore
        return cls.construct(
            participant_code=raw.get('participant_code'),
            ranking=raw.get('ranking'),
            kart_number=raw.get('kart_number'),
            team_name=raw.get('team_name'),
            driver_name=raw.get('driver_name'),
            last_lap_time=raw.get('last_lap_time'),
            best_time=raw.get('best_time'),
            gap=raw.get('gap'),
            interval=raw.get('interval'),
            laps=raw.get('laps'),
            pits=raw.get('pits'),
            pit_time=raw.get('pit_time'),
        )


class InitialData(DictModel):
    """Details about the initial data of a competition."""

    competition_code: str
    reference_time: Optional[int]
    reference_current_offset: Optional[int]
    stage: CompetitionStage
    status: CompetitionStatus
    remaining_length: DiffLap
    participants: Dict[str, Participant] = Field(default_factory=dict)
    parsers_settings: Dict[ParserSettings, str] = Field(default_factory=dict)

    @classmethod
    def from_dict(cls, raw: dict) -> BaseModel:  # noqa: ANN102
        """Return an instance of itself with the data in the dictionary."""
        DictModel._validate_base_dict(cls, raw)  # type: ignore

        raw_participants = raw.get('participants')
        if not isinstance(raw_participants, dict):
            raise Exception('The participants must be a dictionary.')
        participants = {code: Participant.from_dict(p)
                        for code, p in raw_participants.items()}

        parsers_settings: Dict[str, str] = raw.get('parsers_settings', {})
        remaining_length: dict = raw.get('remaining_length')  # type: ignore
        return cls.construct(
            competition_code=raw.get('competition_code'),
            reference_time=raw.get('reference_time', None),
            reference_current_offset=raw.get('reference_current_offset', None),
            stage=CompetitionStage(raw.get('stage')),
            status=CompetitionStatus(raw.get('status')),
            remaining_length=DiffLap.from_dict(remaining_length),
            participants=participants,
            parsers_settings={ParserSettings(k): v
                              for k, v in parsers_settings.items()},
        )

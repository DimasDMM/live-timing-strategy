from pydantic import Field, root_validator
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
    number: int
    team_id: int
    total_driving_time: int
    partial_driving_time: int

    @classmethod
    def from_dict(cls, raw: dict) -> BaseModel:  # noqa: ANN102
        """Return an instance of itself with the data in the dictionary."""
        DictModel._validate_base_dict(cls, raw)  # type: ignore
        return cls.construct(
            id=raw.get('id'),
            participant_code=raw.get('participant_code'),
            name=raw.get('name'),
            number=raw.get('number'),
            team_id=raw.get('team_id'),
            total_driving_time=raw.get('total_driving_time'),
            partial_driving_time=raw.get('partial_driving_time'),
        )


class Team(DictModel):
    """Info of a team."""

    id: int
    participant_code: str
    name: str
    number: int

    @classmethod
    def from_dict(cls, raw: dict) -> BaseModel:  # noqa: ANN102
        """Return an instance of itself with the data in the dictionary."""
        DictModel._validate_base_dict(cls, raw)  # type: ignore
        return cls.construct(
            id=raw.get('id'),
            participant_code=raw.get('participant_code'),
            name=raw.get('name'),
            number=raw.get('number'),
        )


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

    best_time: int
    gap: DiffLap
    interval: DiffLap
    kart_number: int
    laps: int
    last_lap_time: int
    number_pits: int
    participant_code: str
    ranking: int
    driver_name: Optional[str] = Field(default=None)
    team_name: Optional[str] = Field(default=None)
    pit_time: Optional[int] = Field(default=None)

    @root_validator
    def name_is_set(cls, values: dict) -> dict:  # noqa: N805, U100
        """Validate that at least one name is set."""
        driver_name = values.get('driver_name')
        team_name = values.get('team_name')
        if driver_name is None and team_name is None:
            raise ValueError('Both driver and team name cannot be null.')
        return values

    @classmethod
    def from_dict(cls, raw: dict) -> BaseModel:  # noqa: ANN102
        """Return an instance of itself with the data in the dictionary."""
        DictModel._validate_base_dict(cls, raw)  # type: ignore
        return cls.construct(
            best_time=raw.get('best_time'),
            driver_name=raw.get('driver_name'),
            gap=DiffLap.from_dict(raw.get('gap')),  # type: ignore
            interval=DiffLap.from_dict(raw.get('interval')),  # type: ignore
            kart_number=raw.get('kart_number'),
            laps=raw.get('laps'),
            last_lap_time=raw.get('last_lap_time'),
            number_pits=raw.get('number_pits'),
            participant_code=raw.get('participant_code'),
            pit_time=raw.get('pit_time'),
            ranking=raw.get('ranking'),
            team_name=raw.get('team_name'),
        )


class ParticipantTiming(DictModel):
    """Timing details of a participant."""

    best_time: int
    gap: DiffLap
    interval: DiffLap
    kart_number: int
    laps: int
    last_lap_time: int
    number_pits: int
    participant_code: str
    ranking: int
    driver_id: Optional[int] = Field(default=None)
    team_id: Optional[int] = Field(default=None)
    pit_time: Optional[int] = Field(default=None)

    @root_validator
    def name_is_set(cls, values: dict) -> dict:  # noqa: N805, U100
        """Validate that at least one name is set."""
        driver_name = values.get('driver_name')
        team_name = values.get('team_name')
        if driver_name is None and team_name is None:
            raise ValueError('Both driver and team name cannot be null.')
        return values

    @classmethod
    def from_dict(cls, raw: dict) -> BaseModel:  # noqa: ANN102
        """Return an instance of itself with the data in the dictionary."""
        DictModel._validate_base_dict(cls, raw)  # type: ignore
        return cls.construct(
            best_time=raw.get('best_time'),
            driver_name=raw.get('driver_id'),
            gap=DiffLap.from_dict(raw.get('gap')),  # type: ignore
            interval=DiffLap.from_dict(raw.get('interval')),  # type: ignore
            kart_number=raw.get('kart_number'),
            laps=raw.get('laps'),
            last_lap_time=raw.get('last_lap_time'),
            number_pits=raw.get('number_pits'),
            participant_code=raw.get('participant_code'),
            pit_time=raw.get('pit_time'),
            ranking=raw.get('ranking'),
            team_name=raw.get('team_id'),
        )


class CompetitionInfo(BaseModel):
    """Info of a competition."""

    id: Optional[int]
    competition_code: str
    parser_settings: Dict[ParserSettings, str] = Field(default_factory=dict)
    drivers: List[Driver] = Field(default_factory=list)
    teams: List[Team] = Field(default_factory=list)
    timing: Dict[str, ParticipantTiming] = Field(default_factory=dict)


class InitialData(DictModel):
    """Details about the initial data of a competition."""

    competition_code: str
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
            stage=CompetitionStage(raw.get('stage')),
            status=CompetitionStatus(raw.get('status')),
            remaining_length=DiffLap.from_dict(remaining_length),
            participants=participants,
            parsers_settings={ParserSettings(k): v
                              for k, v in parsers_settings.items()},
        )


class UpdateDriver(DictModel):
    """Info update of a driver."""

    id: Optional[int]
    competition_code: str
    participant_code: str
    name: str
    number: int
    team_id: int

    @classmethod
    def from_dict(cls, raw: dict) -> BaseModel:  # noqa: ANN102
        """Return an instance of itself with the data in the dictionary."""
        DictModel._validate_base_dict(cls, raw)  # type: ignore
        return cls.construct(
            id=raw.get('id'),
            competition_code=raw.get('competition_code'),
            participant_code=raw.get('participant_code'),
            name=raw.get('name'),
            number=raw.get('number'),
            team_id=raw.get('team_id'),
        )


class UpdateTeam(DictModel):
    """Info update of a team."""

    id: Optional[int]
    competition_code: str
    participant_code: str
    name: str
    number: int

    @classmethod
    def from_dict(cls, raw: dict) -> BaseModel:  # noqa: ANN102
        """Return an instance of itself with the data in the dictionary."""
        DictModel._validate_base_dict(cls, raw)  # type: ignore
        return cls.construct(
            id=raw.get('id'),
            competition_code=raw.get('competition_code'),
            participant_code=raw.get('participant_code'),
            name=raw.get('name'),
            number=raw.get('number'),
        )

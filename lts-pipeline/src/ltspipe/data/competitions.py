from pydantic import Field, root_validator
from typing import Dict, List, Optional

from ltspipe.base import BaseModel, EnumBase
from ltspipe.data.enum import (
    KartStatus,
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
    position: int
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
            position=raw.get('position'),
            team_name=raw.get('team_name'),
        )


class ParticipantTiming(DictModel):
    """Timing details of a participant."""

    best_time: int
    gap: Optional[DiffLap]
    fixed_kart_status: Optional[KartStatus]
    interval: Optional[DiffLap]
    kart_status: KartStatus
    lap: int
    last_time: int
    number_pits: int
    participant_code: str
    position: int
    stage: CompetitionStage
    driver_id: Optional[int] = Field(default=None)
    pit_time: Optional[int] = Field(default=None)
    team_id: Optional[int] = Field(default=None)

    @root_validator
    def name_is_set(cls, values: dict) -> dict:  # noqa: N805, U100
        """Validate that at least one name is set."""
        driver_id = values.get('driver_id')
        team_id = values.get('team_id')
        if driver_id is None and team_id is None:
            raise ValueError('Both driver and team ID cannot be null.')
        return values

    @classmethod
    def from_dict(cls, raw: dict) -> BaseModel:  # noqa: ANN102
        """Return an instance of itself with the data in the dictionary."""
        DictModel._validate_base_dict(
            cls, raw, ignore_unknowns=True)  # type: ignore

        # Patch gap and interval if necessary
        if raw.get('gap') is None:
            gap = None
        elif 'gap_unit' in raw:
            raw_gap = {
                'value': raw.get('gap'),
                'unit': raw.get('gap_unit'),
            }
            gap = DiffLap.from_dict(raw_gap)
        else:
            gap = DiffLap.from_dict(raw['gap'])

        if raw.get('interval') is None:
            interval = None
        elif 'interval_unit' in raw:
            raw_interval = {
                'value': raw.get('interval'),
                'unit': raw.get('interval_unit'),
            }
            interval = DiffLap.from_dict(raw_interval)
        else:
            interval = DiffLap.from_dict(raw['interval'])

        fixed_kart_status = raw.get('fixed_kart_status')
        return cls.construct(
            best_time=raw.get('best_time'),
            driver_id=raw.get('driver_id'),
            fixed_kart_status=(None if fixed_kart_status is None
                               else KartStatus(fixed_kart_status)),
            kart_status=KartStatus(raw.get('kart_status')),
            gap=gap,  # type: ignore
            interval=interval,  # type: ignore
            lap=raw.get('lap'),
            last_time=raw.get('last_time'),
            number_pits=raw.get('number_pits'),
            participant_code=raw.get('participant_code'),
            pit_time=raw.get('pit_time'),
            position=raw.get('position'),
            stage=CompetitionStage(raw.get('stage')),
            team_id=raw.get('team_id'),
        )


class CompetitionInfo(BaseModel):
    """Info of a competition."""

    id: Optional[int]
    competition_code: str
    parser_settings: Dict[ParserSettings, str] = Field(default_factory=dict)
    drivers: List[Driver] = Field(default_factory=list)
    teams: List[Team] = Field(default_factory=list)
    timing: Dict[str, ParticipantTiming] = Field(default_factory=dict)


class CompetitionMetadata(DictModel):
    """Metadata of a competition."""

    stage: CompetitionStage
    status: CompetitionStatus
    remaining_length: DiffLap

    @classmethod
    def from_dict(cls, raw: dict) -> BaseModel:  # noqa: ANN102
        """Return an instance of itself with the data in the dictionary."""
        # Two ways of building the diff time: it is already a dict or we have to
        # put the parts together
        if ('remaining_length' in raw
                and isinstance(raw['remaining_length'], dict)):
            DictModel._validate_base_dict(cls, raw)  # type: ignore
            remaining_length: dict = raw.get('remaining_length')  # type: ignore
        else:
            remaining_length_unit = raw.get('remaining_length_unit')
            del raw['remaining_length_unit']
            DictModel._validate_base_dict(cls, raw)  # type: ignore
            remaining_length = {
                'value': raw.get('remaining_length'),
                'unit': remaining_length_unit,
            }

        return cls.construct(
            stage=CompetitionStage(raw.get('stage')),
            status=CompetitionStatus(raw.get('status')),
            remaining_length=DiffLap.from_dict(remaining_length),
        )


class UpdateCompetitionMetadataStatus(DictModel):
    """Status of a competition metadata."""

    competition_code: str
    status: CompetitionStatus

    @classmethod
    def from_dict(cls, raw: dict) -> BaseModel:  # noqa: ANN102
        """Return an instance of itself with the data in the dictionary."""
        DictModel._validate_base_dict(cls, raw)  # type: ignore
        return cls.construct(
            competition_code=raw.get('competition_code'),
            status=CompetitionStatus(raw.get('status')),
        )


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


class PitIn(DictModel):
    """Info about a pit-in."""

    id: int
    team_id: Optional[int]
    driver_id: Optional[int]
    lap: int
    pit_time: int
    kart_status: KartStatus
    fixed_kart_status: Optional[KartStatus]
    has_pit_out: bool

    @classmethod
    def from_dict(cls, raw: dict) -> BaseModel:  # noqa: ANN102
        """Return an instance of itself with the data in the dictionary."""
        DictModel._validate_base_dict(cls, raw)  # type: ignore
        fixed_kart_status = raw.get('fixed_kart_status')
        return cls.construct(
            id=raw.get('id'),
            team_id=raw.get('team_id'),
            driver_id=raw.get('driver_id'),
            lap=raw.get('lap'),
            pit_time=raw.get('pit_time'),
            kart_status=KartStatus(raw.get('kart_status')),
            fixed_kart_status=(None if fixed_kart_status is None
                               else KartStatus(fixed_kart_status)),
            has_pit_out=raw.get('has_pit_out'),
        )


class PitOut(DictModel):
    """Info about a pit-out."""

    id: int
    team_id: Optional[int]
    driver_id: Optional[int]
    kart_status: KartStatus
    fixed_kart_status: Optional[KartStatus]

    @classmethod
    def from_dict(cls, raw: dict) -> BaseModel:  # noqa: ANN102
        """Return an instance of itself with the data in the dictionary."""
        DictModel._validate_base_dict(cls, raw)  # type: ignore
        fixed_kart_status = raw.get('fixed_kart_status')
        return cls.construct(
            id=raw.get('id'),
            team_id=raw.get('team_id'),
            driver_id=raw.get('driver_id'),
            kart_status=KartStatus(raw.get('kart_status')),
            fixed_kart_status=(None if fixed_kart_status is None
                               else KartStatus(fixed_kart_status)),
        )


class AddPitIn(DictModel):
    """Info to add a pit-in."""

    competition_code: str
    team_id: Optional[int]
    driver_id: Optional[int]
    lap: int
    pit_time: int
    kart_status: KartStatus

    @classmethod
    def from_dict(cls, raw: dict) -> BaseModel:  # noqa: ANN102
        """Return an instance of itself with the data in the dictionary."""
        DictModel._validate_base_dict(cls, raw)  # type: ignore
        return cls.construct(
            competition_code=raw.get('competition_code'),
            team_id=raw.get('team_id'),
            driver_id=raw.get('driver_id'),
            lap=raw.get('lap'),
            pit_time=raw.get('pit_time'),
            kart_status=KartStatus(raw.get('kart_status')),
        )


class AddPitOut(DictModel):
    """Info to add a pit-out."""

    competition_code: str
    team_id: Optional[int]
    driver_id: Optional[int]
    kart_status: KartStatus

    @classmethod
    def from_dict(cls, raw: dict) -> BaseModel:  # noqa: ANN102
        """Return an instance of itself with the data in the dictionary."""
        DictModel._validate_base_dict(cls, raw)  # type: ignore
        return cls.construct(
            competition_code=raw.get('competition_code'),
            team_id=raw.get('team_id'),
            driver_id=raw.get('driver_id'),
            kart_status=KartStatus(raw.get('kart_status')),
        )


class UpdateDriver(DictModel):
    """Info to update of a driver data."""

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
    """Info to update of a team data."""

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


class UpdateTimingPosition(DictModel):
    """Info to update the timing position of a team."""

    competition_code: str
    team_id: int
    position: int
    auto_other_positions: bool

    @classmethod
    def from_dict(cls, raw: dict) -> BaseModel:  # noqa: ANN102
        """Return an instance of itself with the data in the dictionary."""
        DictModel._validate_base_dict(cls, raw)  # type: ignore
        return cls.construct(
            competition_code=raw.get('competition_code'),
            team_id=raw.get('team_id'),
            position=raw.get('position'),
            auto_other_positions=raw.get('auto_other_positions'),
        )

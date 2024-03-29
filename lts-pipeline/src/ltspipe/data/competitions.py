from pydantic import Field, model_validator
from typing import Any, Dict, List, Optional

from ltspipe.data.base import BaseModel, DictModel
from ltspipe.data.enum import (
    CompetitionStage,
    CompetitionStatus,
    KartStatus,
    LengthUnit,
    ParserSettings,
)
from ltspipe.exceptions import LtsError


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
        return cls.model_construct(
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
        return cls.model_construct(
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
        return cls.model_construct(
            value=raw.get('value'),
            unit=LengthUnit(raw.get('unit')),
        )


class Participant(DictModel):
    """Details of a participant."""

    best_time: int
    gap: Optional[DiffLap]
    kart_number: int
    laps: int
    last_time: int
    number_pits: int
    participant_code: str
    position: int
    driver_name: Optional[str] = Field(default=None)
    interval: Optional[DiffLap] = Field(default=None)
    team_name: Optional[str] = Field(default=None)
    pit_time: Optional[int] = Field(default=None)

    @model_validator(mode='before')
    def name_is_set(cls, values: Dict[str, Any]) -> dict:  # noqa: N805, U100
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
        return cls.model_construct(
            best_time=raw.get('best_time'),
            driver_name=raw.get('driver_name'),
            gap=DiffLap.from_dict(raw.get('gap')),  # type: ignore
            interval=DiffLap.from_dict(raw.get('interval')),  # type: ignore
            kart_number=raw.get('kart_number'),
            laps=raw.get('laps'),
            last_time=raw.get('last_time'),
            number_pits=raw.get('number_pits'),
            participant_code=raw.get('participant_code'),
            pit_time=raw.get('pit_time'),
            position=raw.get('position'),
            team_name=raw.get('team_name'),
        )


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

        return cls.model_construct(
            stage=CompetitionStage(raw.get('stage')),
            status=CompetitionStatus(raw.get('status')),
            remaining_length=DiffLap.from_dict(remaining_length),
        )


class UpdateCompetitionMetadataRemaining(DictModel):
    """Remaining length of a competition metadata."""

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

        return cls.model_construct(
            remaining_length=DiffLap.from_dict(remaining_length),
        )


class UpdateCompetitionMetadataStatus(DictModel):
    """Status of a competition metadata."""

    status: CompetitionStatus

    @classmethod
    def from_dict(cls, raw: dict) -> BaseModel:  # noqa: ANN102
        """Return an instance of itself with the data in the dictionary."""
        DictModel._validate_base_dict(cls, raw)  # type: ignore
        return cls.model_construct(
            status=CompetitionStatus(raw.get('status')),
        )


class InitialData(DictModel):
    """Details about the initial data of a competition."""

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
            raise LtsError('The participants must be a dictionary.')
        participants = {code: Participant.from_dict(p)
                        for code, p in raw_participants.items()}

        parsers_settings: Dict[str, str] = raw.get('parsers_settings', {})
        remaining_length: dict = raw.get('remaining_length')  # type: ignore
        return cls.model_construct(
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
        return cls.model_construct(
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
        return cls.model_construct(
            id=raw.get('id'),
            team_id=raw.get('team_id'),
            driver_id=raw.get('driver_id'),
            kart_status=KartStatus(raw.get('kart_status')),
            fixed_kart_status=(None if fixed_kart_status is None
                               else KartStatus(fixed_kart_status)),
        )


class AddPitIn(DictModel):
    """Info to add a pit-in."""

    team_id: int

    @classmethod
    def from_dict(cls, raw: dict) -> BaseModel:  # noqa: ANN102
        """Return an instance of itself with the data in the dictionary."""
        DictModel._validate_base_dict(cls, raw)  # type: ignore
        return cls.model_construct(
            team_id=raw.get('team_id'),
        )


class AddPitOut(DictModel):
    """Info to add a pit-out."""

    team_id: int

    @classmethod
    def from_dict(cls, raw: dict) -> BaseModel:  # noqa: ANN102
        """Return an instance of itself with the data in the dictionary."""
        DictModel._validate_base_dict(cls, raw)  # type: ignore
        return cls.model_construct(
            team_id=raw.get('team_id'),
        )


class UpdateDriver(DictModel):
    """Info to update of a driver data."""

    id: Optional[int]
    participant_code: str
    name: str
    number: int
    team_id: int
    partial_driving_time: Optional[int] = Field(default=None)
    total_driving_time: Optional[int] = Field(default=None)
    auto_compute_total: bool = Field(default=False)

    @classmethod
    def from_dict(cls, raw: dict) -> BaseModel:  # noqa: ANN102
        """Return an instance of itself with the data in the dictionary."""
        DictModel._validate_base_dict(cls, raw)  # type: ignore
        return cls.model_construct(
            id=raw.get('id'),
            participant_code=raw.get('participant_code'),
            name=raw.get('name'),
            number=raw.get('number'),
            team_id=raw.get('team_id'),
            partial_driving_time=raw.get('partial_driving_time', None),
            total_driving_time=raw.get('total_driving_time', None),
            auto_compute_total=raw.get('auto_compute_total', False),
        )


class UpdateTeam(DictModel):
    """Info to update of a team data."""

    id: Optional[int]
    participant_code: str
    name: str
    number: int

    @classmethod
    def from_dict(cls, raw: dict) -> BaseModel:  # noqa: ANN102
        """Return an instance of itself with the data in the dictionary."""
        DictModel._validate_base_dict(cls, raw)  # type: ignore
        return cls.model_construct(
            id=raw.get('id'),
            participant_code=raw.get('participant_code'),
            name=raw.get('name'),
            number=raw.get('number'),
        )


class UpdateDriverPartialDrivingTime(DictModel):
    """Info to update of a driver data."""

    id: int
    partial_driving_time: int
    auto_compute_total: bool

    @classmethod
    def from_dict(cls, raw: dict) -> BaseModel:  # noqa: ANN102
        """Return an instance of itself with the data in the dictionary."""
        DictModel._validate_base_dict(cls, raw)  # type: ignore
        return cls.model_construct(
            id=raw.get('id'),
            partial_driving_time=raw.get('partial_driving_time'),
            auto_compute_total=raw.get('auto_compute_total'),
        )


class Timing(DictModel):
    """Info about timing."""

    best_time: int
    driver_id: Optional[int]
    fixed_kart_status: Optional[KartStatus]
    gap: Optional[DiffLap]
    interval: Optional[DiffLap]
    kart_status: KartStatus
    lap: Optional[int]
    last_time: int
    number_pits: Optional[int]
    participant_code: str
    pit_time: Optional[int]
    position: int
    stage: CompetitionStage
    team_id: Optional[int]

    @model_validator(mode='before')
    def name_is_set(cls, values: Dict[str, Any]) -> dict:  # noqa: N805, U100
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
        gap: Optional[DiffLap] = None
        if raw.get('gap') is not None:
            if 'gap_unit' in raw:
                raw_gap = {
                    'value': raw.get('gap'),
                    'unit': raw.get('gap_unit'),
                }
                gap = DiffLap.from_dict(raw_gap)  # type: ignore
            else:
                gap = DiffLap.from_dict(raw['gap'])  # type: ignore

        interval: Optional[DiffLap] = None
        if raw.get('interval') is not None:
            if 'interval_unit' in raw:
                raw_interval = {
                    'value': raw.get('interval'),
                    'unit': raw.get('interval_unit'),
                }
                interval = DiffLap.from_dict(raw_interval)  # type: ignore
            else:
                interval = DiffLap.from_dict(raw['interval'])  # type: ignore

        fixed_kart_status = raw.get('fixed_kart_status')
        return cls.model_construct(
            best_time=raw.get('best_time'),
            driver_id=raw.get('driver_id'),
            fixed_kart_status=(None if fixed_kart_status is None
                               else KartStatus(fixed_kart_status)),
            kart_status=KartStatus(raw.get('kart_status')),
            gap=gap,
            interval=interval,
            lap=raw.get('lap'),
            last_time=raw.get('last_time'),
            number_pits=raw.get('number_pits'),
            participant_code=raw.get('participant_code'),
            pit_time=raw.get('pit_time'),
            position=raw.get('position'),
            stage=CompetitionStage(raw.get('stage')),
            team_id=raw.get('team_id'),
        )


class UpdateTimingBestTime(DictModel):
    """Info to update the timing best time of a team."""

    team_id: int
    best_time: int

    @classmethod
    def from_dict(cls, raw: dict) -> BaseModel:  # noqa: ANN102
        """Return an instance of itself with the data in the dictionary."""
        DictModel._validate_base_dict(cls, raw)  # type: ignore
        return cls.model_construct(
            team_id=raw.get('team_id'),
            best_time=raw.get('best_time'),
        )


class UpdateTimingLap(DictModel):
    """Info to update the timing lap of a team."""

    team_id: int
    lap: int

    @classmethod
    def from_dict(cls, raw: dict) -> BaseModel:  # noqa: ANN102
        """Return an instance of itself with the data in the dictionary."""
        DictModel._validate_base_dict(cls, raw)  # type: ignore
        return cls.model_construct(
            team_id=raw.get('team_id'),
            lap=raw.get('lap'),
        )


class UpdateTimingLastTime(DictModel):
    """Info to update the timing last time of a team."""

    team_id: int
    last_time: int
    auto_best_time: bool

    @classmethod
    def from_dict(cls, raw: dict) -> BaseModel:  # noqa: ANN102
        """Return an instance of itself with the data in the dictionary."""
        DictModel._validate_base_dict(cls, raw)  # type: ignore
        return cls.model_construct(
            team_id=raw.get('team_id'),
            last_time=raw.get('last_time'),
            auto_best_time=raw.get('auto_best_time'),
        )


class UpdateTimingNumberPits(DictModel):
    """Info to update the timing number of pits of a team."""

    team_id: int
    number_pits: int

    @classmethod
    def from_dict(cls, raw: dict) -> BaseModel:  # noqa: ANN102
        """Return an instance of itself with the data in the dictionary."""
        DictModel._validate_base_dict(cls, raw)  # type: ignore
        return cls.model_construct(
            team_id=raw.get('team_id'),
            number_pits=raw.get('number_pits'),
        )


class UpdateTimingPitTime(DictModel):
    """Info to update the timing pit time of a team."""

    team_id: int
    pit_time: int

    @classmethod
    def from_dict(cls, raw: dict) -> BaseModel:  # noqa: ANN102
        """Return an instance of itself with the data in the dictionary."""
        DictModel._validate_base_dict(cls, raw)  # type: ignore
        return cls.model_construct(
            team_id=raw.get('team_id'),
            pit_time=raw.get('pit_time'),
        )


class UpdateTimingPosition(DictModel):
    """Info to update the timing position of a team."""

    team_id: int
    position: int
    auto_other_positions: bool

    @classmethod
    def from_dict(cls, raw: dict) -> BaseModel:  # noqa: ANN102
        """Return an instance of itself with the data in the dictionary."""
        DictModel._validate_base_dict(cls, raw)  # type: ignore
        return cls.model_construct(
            team_id=raw.get('team_id'),
            position=raw.get('position'),
            auto_other_positions=raw.get('auto_other_positions'),
        )


class CompetitionInfo(BaseModel):
    """Info of a competition."""

    id: int
    competition_code: str
    parser_settings: Dict[ParserSettings, str]
    drivers: List[Driver]
    teams: Dict[str, Team]
    timing: Dict[str, Timing]

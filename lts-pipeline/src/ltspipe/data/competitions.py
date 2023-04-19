from pydantic import Field
from typing import Dict, Optional

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


class CompetitionInfo(BaseModel):
    """Info of a competition."""

    id: Optional[int]
    competition_code: str
    parser_settings: Dict[ParserSettings, str] = Field(default_factory=dict)


class DiffLap(BaseModel):
    """Difference between two laps."""

    value: int
    unit: LengthUnit


class Participant(DictModel):
    """Details of a participant."""

    participant_code: str
    ranking: Optional[int] = Field(default=None)
    kart_number: Optional[int] = Field(default=None)
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

    reference_time: Optional[int]
    reference_current_offset: Optional[int]
    stage: CompetitionStage
    status: CompetitionStatus
    remaining_length: DiffLap
    participants: Dict[str, Participant]
    parsers_settings: Optional[Dict[ParserSettings, str]]

    @classmethod
    def from_dict(cls, raw: dict) -> BaseModel:  # noqa: ANN102
        """Return an instance of itself with the data in the dictionary."""
        DictModel._validate_base_dict(cls, raw)  # type: ignore

        raw_participants = raw.get('participants')
        if not isinstance(raw_participants, dict):
            raise Exception('The participants must be a dictionary.')
        participants = {code: Participant.from_dict(p)
                        for code, p in raw_participants.items()}

        return cls.construct(
            reference_time=raw.get('reference_time', None),
            reference_current_offset=raw.get('reference_current_offset', None),
            stage=CompetitionStage(raw.get('stage')),
            status=CompetitionStatus(raw.get('status')),
            remaining_length=raw.get('remaining_length'),
            participants=participants,
            parsers_settings=raw.get('parsers_settings', None),
        )

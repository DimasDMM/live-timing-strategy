from pydantic import Field
from typing import Dict, Optional

from ltspipe.base import BaseModel
from ltspipe.data.enum import (
    CompetitionStage,
    CompetitionStatus,
    LengthUnit,
    ParserSettings,
)


class CompetitionInfo(BaseModel):
    """Info of a competition."""

    id: Optional[int]
    competition_code: str
    parser_settings: Dict[ParserSettings, str] = Field(default_factory=dict)


class DiffLap(BaseModel):
    """Difference between two laps."""

    value: int
    unit: LengthUnit


class Participant(BaseModel):
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


class InitialData(BaseModel):
    """Details about the initial data of a competition."""

    reference_time: Optional[int]
    reference_current_offset: Optional[int]
    stage: CompetitionStage
    status: CompetitionStatus
    remaining_length: DiffLap
    participants: Dict[str, Participant]
    parsers_settings: Optional[Dict[ParserSettings, str]]

from datetime import datetime
from typing import Optional

from ltsapi.models import BaseModel
from ltsapi.models.enum import (
    CompetitionStage,
    CompetitionStatus,
    LengthUnit,
)
from ltsapi.models.tracks import GetTrack


class AddCompetitionMetadata(BaseModel):
    """Metadata of a competition."""

    status: CompetitionStatus
    stage: CompetitionStage
    remaining_length: int
    remaining_length_unit: LengthUnit


class GetCompetitionMetadata(BaseModel):
    """Metadata of a competition."""

    status: CompetitionStatus
    stage: CompetitionStage
    remaining_length: int
    remaining_length_unit: LengthUnit
    insert_date: datetime
    update_date: datetime


class UpdateCompetitionMetadata(BaseModel):
    """Update the metadata of a competition."""

    status: CompetitionStatus
    stage: CompetitionStage
    remaining_length: int
    remaining_length_unit: LengthUnit


class AddCompetitionSettings(BaseModel):
    """Add the settings of a competition."""

    length: int
    length_unit: LengthUnit
    pit_time: Optional[int]
    min_number_pits: int


class GetCompetitionSettings(BaseModel):
    """Settings of a competition."""

    length: int
    length_unit: LengthUnit
    pit_time: Optional[int]
    min_number_pits: int
    insert_date: datetime
    update_date: datetime


class UpdateCompetitionSettings(BaseModel):
    """Update the settings of a competition."""

    length: int
    length_unit: LengthUnit
    pit_time: Optional[int]
    min_number_pits: int


class AddCompetition(BaseModel):
    """Data to add a new competition."""

    track_id: int
    competition_code: str
    name: str
    description: str
    settings: AddCompetitionSettings


class GetCompetition(BaseModel):
    """All data of a competition."""

    id: int
    track: GetTrack
    competition_code: str
    name: str
    description: str
    insert_date: datetime
    update_date: datetime


class UpdateRemainingLength(BaseModel):
    """Update the remaining length of a competition."""

    remaining_length: int
    remaining_length_unit: LengthUnit


class UpdateStage(BaseModel):
    """Update the stage of a competition."""

    stage: CompetitionStage


class UpdateStatus(BaseModel):
    """Update the status of a competition."""

    status: CompetitionStatus

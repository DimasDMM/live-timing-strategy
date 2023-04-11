from datetime import datetime
from pydantic import BaseModel
from typing import Optional

from ltsapi.models.timing import LengthUnit


class AddTrack(BaseModel):
    """Data to add a new track."""

    name: str


class GetTrack(BaseModel):
    """Track data."""

    id: int
    name: str
    insert_date: datetime
    update_date: datetime


class UpdateTrack(BaseModel):
    """Data to update a track."""

    name: Optional[str]


class AddCompetitionSettings(BaseModel):
    """Add the settings of a competition."""

    length: int
    length_unit: LengthUnit
    pit_time: Optional[int]
    min_number_pits: int


class GetCompetitionSettings(BaseModel):
    """Settings of a competition."""

    competition_id: int
    length: int
    length_unit: LengthUnit
    pit_time: Optional[int]
    min_number_pits: int
    insert_date: datetime
    update_date: datetime


class UpdateCompetitionSettings(BaseModel):
    """Update the settings of a competition."""

    length: Optional[int]
    length_unit: Optional[LengthUnit]
    pit_time: Optional[int]
    min_number_pits: Optional[int]


class AddCompetition(BaseModel):
    """Data to add a new competition."""

    track_id: int
    competition_code: str
    name: str
    description: str


class GetCompetition(BaseModel):
    """All data of a competition."""

    id: int
    track: GetTrack
    competition_code: str
    name: str
    description: str
    insert_date: datetime
    update_date: datetime

from datetime import datetime
from pydantic import BaseModel


class GetTrack(BaseModel):
    """Track data."""

    id: int
    name: str
    insert_date: datetime
    update_date: datetime


class AddCompetition(BaseModel):
    """Data to add a new competition."""

    track_id: int
    code: str
    name: str
    description: str


class GetCompetition(BaseModel):
    """All data of a competition."""

    id: int
    track: GetTrack
    code: str
    name: str
    description: str
    insert_date: datetime
    update_date: datetime

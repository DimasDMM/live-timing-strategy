from datetime import datetime
from pydantic import BaseModel


class FullTrack(BaseModel):
    """Track data."""

    id: int
    name: str
    insert_date: datetime
    update_date: datetime


class FullCompetition(BaseModel):
    """Competition data."""

    id: int
    track: FullTrack
    code: str
    name: str
    description: str
    insert_date: datetime
    update_date: datetime

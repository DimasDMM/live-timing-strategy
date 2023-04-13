from datetime import datetime
from typing import Optional

from ltsapi.models import BaseModel


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

from datetime import datetime
from typing import Optional

from ltsapi.models import BaseModel


class AddDriver(BaseModel):
    """Data to add a new driver."""

    participant_code: str
    name: str
    number: Optional[int]


class GetDriver(BaseModel):
    """All data of a driver."""

    id: int
    competition_id: int
    team_id: Optional[int]
    participant_code: str
    name: str
    number: Optional[int]
    insert_date: datetime
    update_date: datetime


class UpdateDriver(BaseModel):
    """Update the data of a driver."""

    participant_code: str
    name: str
    number: Optional[int]


class AddTeam(BaseModel):
    """Data to add a new team."""

    participant_code: str
    name: str
    number: Optional[int]


class GetTeam(BaseModel):
    """All data of a team."""

    id: int
    competition_id: int
    participant_code: str
    name: str
    number: Optional[int]
    insert_date: datetime
    update_date: datetime


class UpdateTeam(BaseModel):
    """Update the data of a team."""

    participant_code: str
    name: str
    number: Optional[int]

from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional


class AddDriver(BaseModel):
    """Data to add a new driver."""

    participant_code: str
    name: str
    number: Optional[int]
    total_driving_time: Optional[int]
    partial_driving_time: Optional[int]
    reference_time_offset: Optional[int]


class GetDriver(BaseModel):
    """All data of a driver."""

    id: int
    competition_id: int
    team_id: Optional[int]
    participant_code: str
    name: str
    number: Optional[int]
    total_driving_time: int
    partial_driving_time: int
    reference_time_offset: int
    insert_date: datetime
    update_date: datetime


class UpdateDriver(BaseModel):
    """Update the data of a driver."""

    participant_code: Optional[str]
    name: Optional[str]
    number: Optional[int]
    total_driving_time: Optional[int]
    partial_driving_time: Optional[int]
    reference_time_offset: Optional[int]


class AddTeam(BaseModel):
    """Data to add a new team."""

    participant_code: str
    name: str
    number: Optional[int]
    reference_time_offset: Optional[int]


class GetTeam(BaseModel):
    """All data of a team."""

    id: int
    competition_id: int
    participant_code: str
    name: str
    number: Optional[int]
    reference_time_offset: int
    drivers: List[GetDriver]
    insert_date: datetime
    update_date: datetime


class UpdateTeam(BaseModel):
    """Update the data of a team."""

    participant_code: Optional[str]
    name: Optional[str]
    number: Optional[int]
    reference_time_offset: Optional[int]

from enum import Enum
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class LengthUnit(str, Enum):
    """Units to measure the race length."""

    LAPS = 'laps'
    MILLIS = 'millis'


class GetLapTime(BaseModel):
    """Data of a lap."""

    id: int
    competition_id: int
    team_id: Optional[int]
    driver_id: Optional[int]
    position: int
    time: int
    best_time: int
    lap: int
    interval: int
    interval_unit: str
    stage: str
    pits: Optional[int]
    number_pits: int
    insert_date: datetime
    update_date: datetime

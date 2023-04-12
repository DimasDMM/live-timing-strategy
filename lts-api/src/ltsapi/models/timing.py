from datetime import datetime
from typing import Optional

from ltsapi.models import BaseModel
from ltsapi.models.enum import LengthUnit


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
    interval_unit: LengthUnit
    stage: str
    pits: Optional[int]
    number_pits: int
    insert_date: datetime
    update_date: datetime

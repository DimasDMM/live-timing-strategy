from datetime import datetime
from typing import Optional

from ltsapi.models import BaseModel
from ltsapi.models.enum import (
    KartStatus,
    LengthUnit,
)


class AddLapTime(BaseModel):
    """Data of a lap."""

    team_id: Optional[int]
    driver_id: Optional[int]
    position: int
    time: int
    best_time: int
    lap: int
    interval: int
    interval_unit: LengthUnit
    stage: str
    pit_time: Optional[int]
    kart_status: KartStatus
    fixed_kart_status: Optional[KartStatus]
    number_pits: int


class GetLapTime(BaseModel):
    """Data of a lap."""

    team_id: Optional[int]
    driver_id: Optional[int]
    participant_code: str
    position: int
    time: int
    best_time: int
    lap: int
    interval: int
    interval_unit: LengthUnit
    stage: str
    pit_time: Optional[int]
    kart_status: KartStatus
    fixed_kart_status: Optional[KartStatus]
    number_pits: int
    insert_date: datetime
    update_date: datetime


class UpdateLapTime(BaseModel):
    """Data to update a lap record."""

    driver_id: Optional[int]
    position: Optional[int]
    time: int
    best_time: int
    lap: int
    interval: int
    interval_unit: LengthUnit
    stage: str
    pit_time: Optional[int]
    kart_status: KartStatus
    fixed_kart_status: Optional[KartStatus]
    number_pits: int

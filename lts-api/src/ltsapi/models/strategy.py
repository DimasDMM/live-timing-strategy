from datetime import datetime
from typing import List

from ltsapi.models import BaseModel
from ltsapi.models.enum import KartStatus


class AddStrategyPitsStats(BaseModel):
    """Data to add strategy pits stats."""

    pit_in_id: int
    best_time: int
    avg_time: int


class GetStrategyPitsStats(BaseModel):
    """Strategy pits stats."""

    id: int
    pit_in_id: int
    best_time: int
    avg_time: int
    insert_date: datetime
    update_date: datetime


class AddStrategyPitsKarts(BaseModel):
    """Data to add strategy pits karts."""

    competition_id: int
    pit_in_id: int
    step: int
    kart_status: KartStatus
    probability: float


class GetStrategyPitsKarts(BaseModel):
    """Strategy pits karts."""

    id: int
    competition_id: int
    pit_in_id: int
    step: int
    kart_status: KartStatus
    probability: float
    insert_date: datetime
    update_date: datetime

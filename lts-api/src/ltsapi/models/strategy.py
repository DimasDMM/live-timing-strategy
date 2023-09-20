from datetime import datetime
from typing import List

from ltsapi.models import BaseModel
from ltsapi.models.enum import KartStatus


class AddStrategyPitsStats(BaseModel):
    """Data to add strategy pit stats."""

    pit_in_id: int
    best_time: int
    avg_time: int


class GetStrategyPitsStats(BaseModel):
    """Strategy pit stats."""

    id: int
    pit_in_id: int
    best_time: int
    avg_time: int
    insert_date: datetime
    update_date: datetime


class AddStrategyPitKartsItem(BaseModel):
    """Data to add strategy pit karts (item)."""

    competition_id: int
    pit_in_id: int
    step: int
    kart_status: KartStatus
    probability: float


class AddStrategyPitKarts(BaseModel):
    """Data to add strategy pit karts."""

    pit_karts: List[AddStrategyPitKartsItem]


class GetStrategyPitKartsItem(BaseModel):
    """Strategy pit karts (item)."""

    id: int
    competition_id: int
    pit_in_id: int
    step: int
    kart_status: KartStatus
    probability: float
    insert_date: datetime
    update_date: datetime


class GetStrategyPitKarts(BaseModel):
    """Strategy pit karts."""

    pit_karts: List[GetStrategyPitKartsItem]

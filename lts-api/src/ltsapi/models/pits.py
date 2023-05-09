from datetime import datetime
from typing import Optional

from ltsapi.models import BaseModel
from ltsapi.models.enum import KartStatus


class AddPitIn(BaseModel):
    """Data to add a new pit-in."""

    team_id: Optional[int]
    driver_id: Optional[int]
    lap: int
    pit_time: Optional[int]
    kart_status: KartStatus
    fixed_kart_status: Optional[KartStatus]


class AddPitOut(BaseModel):
    """Data to add a new pit-out."""

    team_id: Optional[int]
    driver_id: Optional[int]
    kart_status: KartStatus
    fixed_kart_status: Optional[KartStatus]


class GetPitIn(BaseModel):
    """Pit-in data."""

    id: int
    competition_id: int
    team_id: Optional[int]
    driver_id: Optional[int]
    lap: int
    pit_time: Optional[int]
    kart_status: KartStatus
    fixed_kart_status: Optional[KartStatus]
    insert_date: datetime
    update_date: datetime


class GetPitOut(BaseModel):
    """Pit-out data."""

    id: int
    competition_id: int
    team_id: Optional[int]
    driver_id: Optional[int]
    kart_status: KartStatus
    fixed_kart_status: Optional[KartStatus]
    insert_date: datetime
    update_date: datetime


class UpdatePitIn(BaseModel):
    """Data to update a pit-in."""

    lap: int
    pit_time: Optional[int]
    kart_status: KartStatus
    fixed_kart_status: Optional[KartStatus]


class UpdatePitInPitTime(BaseModel):
    """Data to update the pit time of a pit-in."""

    pit_time: Optional[int]


class UpdatePitInKartStatus(BaseModel):
    """Data to update the kart status of a pit-in."""

    kart_status: KartStatus


class UpdatePitInFixedKartStatus(BaseModel):
    """Data to update the fixed kart status of a pit-in."""

    fixed_kart_status: Optional[KartStatus]


class UpdatePitOut(BaseModel):
    """Data to update a pit-out."""

    kart_status: KartStatus
    fixed_kart_status: Optional[KartStatus]


class UpdatePitOutKartStatus(BaseModel):
    """Data to update the kart status of a pit-out."""

    kart_status: KartStatus


class UpdatePitOutFixedKartStatus(BaseModel):
    """Data to update the fixed kart status of a pit-out."""

    fixed_kart_status: Optional[KartStatus]

from datetime import datetime
from pydantic import Field
from typing import Optional

from ltsapi.models import BaseModel
from ltsapi.models.enum import (
    CompetitionStage,
    KartStatus,
    LengthUnit,
)


class AddTiming(BaseModel):
    """Data of a timing item."""

    team_id: Optional[int]
    driver_id: Optional[int]
    position: int
    last_time: int
    best_time: int
    lap: int
    gap: Optional[int]
    gap_unit: Optional[LengthUnit]
    interval: Optional[int]
    interval_unit: Optional[LengthUnit]
    stage: CompetitionStage
    pit_time: Optional[int]
    kart_status: KartStatus
    fixed_kart_status: Optional[KartStatus]
    number_pits: int


class GetTiming(BaseModel):
    """Data of a timing item."""

    team_id: Optional[int]
    driver_id: Optional[int]
    participant_code: str
    position: int
    last_time: int
    best_time: int
    lap: int
    gap: Optional[int]
    gap_unit: Optional[LengthUnit]
    interval: Optional[int]
    interval_unit: Optional[LengthUnit]
    stage: CompetitionStage
    pit_time: Optional[int]
    kart_status: KartStatus
    fixed_kart_status: Optional[KartStatus]
    number_pits: int
    insert_date: datetime
    update_date: datetime

    def to_adder(self) -> AddTiming:
        """Transform instance into an AddTiming object."""
        return AddTiming(
            team_id=self.team_id,
            driver_id=self.driver_id,
            position=self.position,
            last_time=self.last_time,
            best_time=self.best_time,
            lap=self.lap,
            gap=self.gap,
            gap_unit=self.gap_unit,
            interval=self.interval,
            interval_unit=self.interval_unit,
            stage=self.stage,
            pit_time=self.pit_time,
            kart_status=self.kart_status,
            fixed_kart_status=self.fixed_kart_status,
            number_pits=self.number_pits,
        )


class UpdateTiming(BaseModel):
    """Data to update a timing item."""

    driver_id: Optional[int]
    position: int
    last_time: int
    best_time: int
    lap: int
    gap: Optional[int]
    gap_unit: Optional[LengthUnit]
    interval: Optional[int]
    interval_unit: Optional[LengthUnit]
    stage: CompetitionStage
    pit_time: Optional[int]
    kart_status: KartStatus
    fixed_kart_status: Optional[KartStatus]
    number_pits: int
    # If True, it updates the best-time with the minimum time
    auto_best_time: bool = Field(default=True)
    # If True, it should modify the position of other participants too
    auto_other_positions: bool = Field(default=True)


class UpdateTimingDriver(BaseModel):
    """Data to update the driver of a timing item."""

    driver_id: Optional[int]


class UpdateTimingPosition(BaseModel):
    """Data to update the position of a timing item."""

    position: int
    # If True, it should modify the position of other participants too
    auto_other_positions: bool = Field(default=True)


class UpdateTimingLastTime(BaseModel):
    """Data to update a lap item."""

    last_time: int
    # If True, it updates the best-time with the minimum time
    auto_best_time: bool = Field(default=True)


class UpdateTimingLastTimeWBest(BaseModel):
    """Data to update a lap item."""

    last_time: int
    best_time: int


class UpdateTimingBestTime(BaseModel):
    """Data to update the best time of a timing item."""

    best_time: int


class UpdateTimingLap(BaseModel):
    """Data to update the lap of a timing item."""

    lap: int


class UpdateTimingGap(BaseModel):
    """Data to update the gap of a timing item."""

    gap: Optional[int]
    gap_unit: Optional[LengthUnit]


class UpdateTimingInterval(BaseModel):
    """Data to update the interval of a timing item."""

    interval: Optional[int]
    interval_unit: Optional[LengthUnit]


class UpdateTimingStage(BaseModel):
    """Data to update the stage of a timing item."""

    stage: CompetitionStage


class UpdateTimingPitTime(BaseModel):
    """Data to update the pit time of a timing item."""

    pit_time: Optional[int]


class UpdateTimingKartStatus(BaseModel):
    """Data to update the kart status of a timing item."""

    kart_status: KartStatus


class UpdateTimingFixedKartStatus(BaseModel):
    """Data to update the fixed kart status of a timing item."""

    fixed_kart_status: Optional[KartStatus]


class UpdateTimingNumberPits(BaseModel):
    """Data to update the number of pits of a timing item."""

    number_pits: int

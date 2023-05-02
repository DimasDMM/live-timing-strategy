from fastapi import APIRouter, Path
from typing import Annotated, List, Union

from ltsapi import API_VERSION, _build_logger
from ltsapi.exceptions import ApiError
from ltsapi.managers.timing import TypeUpdateTiming, TimingManager
from ltsapi.models.timing import (
    GetTiming,
    UpdateTiming,
    UpdateTimingDriver,
    UpdateTimingPosition,
    UpdateTimingLastTime,
    UpdateTimingBestTime,
    UpdateTimingLap,
    UpdateTimingGap,
    UpdateTimingInterval,
    UpdateTimingStage,
    UpdateTimingPitTime,
    UpdateTimingKartStatus,
    UpdateTimingFixedKartStatus,
    UpdateTimingNumberPits,
)
from ltsapi.models.responses import Empty
from ltsapi.router import _build_db_connection


router = APIRouter(
    prefix='/' + API_VERSION + '/c/{competition_id}',  # noqa
    tags=['Timing'])
_logger = _build_logger(__package__)


@router.get(
        path='/timing',
        summary='Get current timing in a competition')
async def get_current_global_timing(
    competition_id: Annotated[int, Path(description='ID of the competition')],
) -> List[GetTiming]:
    """Get current timing of a specific competition."""
    db = _build_db_connection(_logger)
    with db:
        manager = TimingManager(db=db, logger=_logger)
        return manager.get_current_all_by_id(competition_id)


@router.get(
        path='/timing/drivers/{driver_id}',  # noqa: FS003
        summary='Get current timing in a competition of a specific driver')
async def get_current_driver_timing(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    driver_id: Annotated[int, Path(description='ID of the driver')],
) -> Union[GetTiming, Empty]:
    """Get current timing in a competition of a specific driver."""
    db = _build_db_connection(_logger)
    with db:
        manager = TimingManager(db=db, logger=_logger)
        item = manager.get_current_single_by_id(
            competition_id, driver_id=driver_id)
        return Empty() if item is None else item


@router.get(
        path='/timing/drivers/{driver_id}/history',  # noqa: FS003
        summary='Get history timing in a competition of a specific driver')
async def get_history_driver_timing(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    driver_id: Annotated[int, Path(description='ID of the driver')],
) -> List[GetTiming]:
    """Get history timing in a competition of a specific driver."""
    db = _build_db_connection(_logger)
    with db:
        manager = TimingManager(db=db, logger=_logger)
        return manager.get_history_by_id(competition_id, driver_id=driver_id)


@router.get(
        path='/timing/teams/{team_id}',  # noqa: FS003
        summary='Get current timing in a competition of a specific team')
async def get_current_team_timing(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    team_id: Annotated[int, Path(description='ID of the team')],
) -> Union[GetTiming, Empty]:
    """Get current timing in a competition of a specific team."""
    db = _build_db_connection(_logger)
    with db:
        manager = TimingManager(db=db, logger=_logger)
        item = manager.get_current_single_by_id(competition_id, team_id=team_id)
        return Empty() if item is None else item


@router.put(
        path='/timing/teams/{team_id}',  # noqa: FS003
        summary='Update the timing of a team')
async def update_timing_by_team(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    team_id: Annotated[int, Path(description='ID of the team')],
    timing: UpdateTiming,
) -> GetTiming:
    """Update the timing of a team."""
    return _update_timing_by_team(competition_id, team_id, timing)


@router.put(
        path='/timing/teams/{team_id}/driver',  # noqa: FS003
        summary='Update the timing (driver) of a team')
async def update_timing_driver_by_team(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    team_id: Annotated[int, Path(description='ID of the team')],
    timing: UpdateTimingDriver,
) -> GetTiming:
    """Update the timing (driver) of a team."""
    return _update_timing_by_team(competition_id, team_id, timing)


@router.put(
        path='/timing/teams/{team_id}/position',  # noqa: FS003
        summary='Update the timing (position) of a team')
async def update_timing_position_by_team(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    team_id: Annotated[int, Path(description='ID of the team')],
    timing: UpdateTimingPosition,
) -> GetTiming:
    """Update the timing (position) of a team."""
    return _update_timing_by_team(competition_id, team_id, timing)


@router.put(
        path='/timing/teams/{team_id}/last_time',  # noqa: FS003
        summary='Update the timing (last time) of a team')
async def update_timing_last_time_by_team(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    team_id: Annotated[int, Path(description='ID of the team')],
    timing: UpdateTimingLastTime,
) -> GetTiming:
    """Update the timing (last time) of a team."""
    return _update_timing_by_team(competition_id, team_id, timing)


@router.put(
        path='/timing/teams/{team_id}/best_time',  # noqa: FS003
        summary='Update the timing (best time) of a team')
async def update_timing_best_time_by_team(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    team_id: Annotated[int, Path(description='ID of the team')],
    timing: UpdateTimingBestTime,
) -> GetTiming:
    """Update the timing (best time) of a team."""
    return _update_timing_by_team(competition_id, team_id, timing)


@router.put(
        path='/timing/teams/{team_id}/lap',  # noqa: FS003
        summary='Update the timing (lap) of a team')
async def update_timing_lap_by_team(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    team_id: Annotated[int, Path(description='ID of the team')],
    timing: UpdateTimingLap,
) -> GetTiming:
    """Update the timing (lap) of a team."""
    return _update_timing_by_team(competition_id, team_id, timing)


@router.put(
        path='/timing/teams/{team_id}/gap',  # noqa: FS003
        summary='Update the timing (gap) of a team')
async def update_timing_gap_by_team(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    team_id: Annotated[int, Path(description='ID of the team')],
    timing: UpdateTimingGap,
) -> GetTiming:
    """Update the timing (gap) of a team."""
    return _update_timing_by_team(competition_id, team_id, timing)


@router.put(
        path='/timing/teams/{team_id}/interval',  # noqa: FS003
        summary='Update the timing (interval) of a team')
async def update_timing_interval_by_team(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    team_id: Annotated[int, Path(description='ID of the team')],
    timing: UpdateTimingInterval,
) -> GetTiming:
    """Update the timing (interval) of a team."""
    return _update_timing_by_team(competition_id, team_id, timing)


@router.put(
        path='/timing/teams/{team_id}/stage',  # noqa: FS003
        summary='Update the timing (stage) of a team')
async def update_timing_stage_by_team(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    team_id: Annotated[int, Path(description='ID of the team')],
    timing: UpdateTimingStage,
) -> GetTiming:
    """Update the timing (stage) of a team."""
    return _update_timing_by_team(competition_id, team_id, timing)


@router.put(
        path='/timing/teams/{team_id}/pit_time',  # noqa: FS003
        summary='Update the timing (pit time) of a team')
async def update_timing_pit_time_by_team(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    team_id: Annotated[int, Path(description='ID of the team')],
    timing: UpdateTimingPitTime,
) -> GetTiming:
    """Update the timing (pit time) of a team."""
    return _update_timing_by_team(competition_id, team_id, timing)


@router.put(
        path='/timing/teams/{team_id}/kart_status',  # noqa: FS003
        summary='Update the timing (kart status) of a team')
async def update_timing_kart_status_by_team(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    team_id: Annotated[int, Path(description='ID of the team')],
    timing: UpdateTimingKartStatus,
) -> GetTiming:
    """Update the timing (kart status) of a team."""
    return _update_timing_by_team(competition_id, team_id, timing)


@router.put(
        path='/timing/teams/{team_id}/fixed_kart_status',  # noqa: FS003
        summary='Update the timing (fixed kart status) of a team')
async def update_timing_fixed_kart_status_by_team(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    team_id: Annotated[int, Path(description='ID of the team')],
    timing: UpdateTimingFixedKartStatus,
) -> GetTiming:
    """Update the timing (fixed kart status) of a team."""
    return _update_timing_by_team(competition_id, team_id, timing)


@router.put(
        path='/timing/teams/{team_id}/number_pits',  # noqa: FS003
        summary='Update the timing (number pits) of a team')
async def update_timing_number_pits_by_team(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    team_id: Annotated[int, Path(description='ID of the team')],
    timing: UpdateTimingNumberPits,
) -> GetTiming:
    """Update the timing (number pits) of a team."""
    return _update_timing_by_team(competition_id, team_id, timing)


def _update_timing_by_team(
        competition_id: int,
        team_id: int,
        timing: TypeUpdateTiming) -> GetTiming:
    """Update the timing (any field) of a team."""
    db = _build_db_connection(_logger)
    with db:
        db.start_transaction()
        manager = TimingManager(db=db, logger=_logger)
        manager.update_by_id(
            timing, competition_id=competition_id, team_id=team_id)
        item = manager.get_current_single_by_id(competition_id, team_id=team_id)
        if item is None:
            raise ApiError('No data was inserted or updated.')
        return item


@router.get(
        path='/timing/teams/{team_id}/history',  # noqa: FS003
        summary='Get history timing in a competition of a specific team')
async def get_history_team_timing(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    team_id: Annotated[int, Path(description='ID of the team')],
) -> List[GetTiming]:
    """Get history timing in a competition of a specific team."""
    db = _build_db_connection(_logger)
    with db:
        manager = TimingManager(db=db, logger=_logger)
        return manager.get_history_by_id(competition_id, team_id=team_id)


@router.get(
        path='/timing/history',
        summary='Get history timing in a competition')
async def get_history_timing(
    competition_id: Annotated[int, Path(description='ID of the competition')],
) -> List[GetTiming]:
    """Get history timing in a competition."""
    db = _build_db_connection(_logger)
    with db:
        manager = TimingManager(db=db, logger=_logger)
        return manager.get_history_by_id(competition_id)

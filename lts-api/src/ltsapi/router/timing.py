from fastapi import APIRouter, Path
from typing import Annotated, List, Union

from ltsapi import API_VERSION, _build_logger
from ltsapi.exceptions import ApiError
from ltsapi.managers.timing import TimingManager
from ltsapi.models.timing import (
    GetLapTime,
    UpdateLapTime,
)
from ltsapi.models.responses import Empty
from ltsapi.router import _build_db_connection


router = APIRouter(
    prefix='/' + API_VERSION + '/competitions/{competition_id}',  # noqa
    tags=['Timing'])
_logger = _build_logger(__package__)


@router.get(
        path='/timing',
        summary='Get current timing in a competition')
async def get_current_global_timing(
    competition_id: Annotated[int, Path(description='ID of the competition')],
) -> List[GetLapTime]:
    """Get current timing of a specific competition."""
    db = _build_db_connection(_logger)
    with db:
        manager = TimingManager(db=db, logger=_logger)
        return manager.get_current_all_by_id(competition_id)


@router.get(
        path='/timing/driver/{driver_id}',  # noqa: FS003
        summary='Get current timing in a competition of a specific driver')
async def get_current_driver_timing(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    driver_id: Annotated[int, Path(description='ID of the driver')],
) -> Union[GetLapTime, Empty]:
    """Get current timing in a competition of a specific driver."""
    db = _build_db_connection(_logger)
    with db:
        manager = TimingManager(db=db, logger=_logger)
        item = manager.get_current_single_by_id(
            competition_id, driver_id=driver_id)
        return Empty() if item is None else item


@router.get(
        path='/timing/driver/{driver_id}/history',  # noqa: FS003
        summary='Get history timing in a competition of a specific driver')
async def get_history_driver_timing(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    driver_id: Annotated[int, Path(description='ID of the driver')],
) -> List[GetLapTime]:
    """Get history timing in a competition of a specific driver."""
    db = _build_db_connection(_logger)
    with db:
        manager = TimingManager(db=db, logger=_logger)
        return manager.get_history_by_id(competition_id, driver_id=driver_id)


@router.get(
        path='/timing/team/{team_id}',  # noqa: FS003
        summary='Get current timing in a competition of a specific team')
async def get_current_team_timing(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    team_id: Annotated[int, Path(description='ID of the team')],
) -> Union[GetLapTime, Empty]:
    """Get current timing in a competition of a specific team."""
    db = _build_db_connection(_logger)
    with db:
        manager = TimingManager(db=db, logger=_logger)
        item = manager.get_current_single_by_id(competition_id, team_id=team_id)
        return Empty() if item is None else item


@router.put(
        path='/timing/team/{team_id}',  # noqa: FS003
        summary='Update the timing of a team in a competition')
async def update_timing_by_team(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    team_id: Annotated[int, Path(description='ID of the team')],
    lap_time: UpdateLapTime,
) -> GetLapTime:
    """Update the timing of a team in a competition."""
    db = _build_db_connection(_logger)
    with db:
        manager = TimingManager(db=db, logger=_logger)
        manager.update_by_id(
            lap_time, competition_id=competition_id, team_id=team_id)
        item = manager.get_current_single_by_id(competition_id, team_id=team_id)
        if item is None:
            raise ApiError('No data was inserted or updated.')
        return item


@router.get(
        path='/timing/team/{team_id}/history',  # noqa: FS003
        summary='Get history timing in a competition of a specific team')
async def get_history_team_timing(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    team_id: Annotated[int, Path(description='ID of the team')],
) -> List[GetLapTime]:
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
) -> List[GetLapTime]:
    """Get history timing in a competition."""
    db = _build_db_connection(_logger)
    with db:
        manager = TimingManager(db=db, logger=_logger)
        return manager.get_history_by_id(competition_id)

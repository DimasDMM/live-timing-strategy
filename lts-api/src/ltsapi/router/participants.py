from fastapi import APIRouter, Path
from typing import Annotated, List, Union

from ltsapi import API_VERSION, _build_logger
from ltsapi.exceptions import ApiError
from ltsapi.managers.participants import DriversManager, TeamsManager
from ltsapi.models.participants import (
    AddDriver,
    AddTeam,
    GetDriver,
    GetTeam,
    UpdateDriver,
    UpdateTeam,
)
from ltsapi.models.responses import Empty
from ltsapi.router import _build_db_connection


router = APIRouter(
    prefix='/' + API_VERSION + '/competitions/{competition_id}',  # noqa
    tags=['Participants'])
_logger = _build_logger(__package__)
_db = _build_db_connection(_logger)


@router.get(
        path='/teams',
        summary='Get all teams in a competition')
async def get_teams_by_competition_id(
    competition_id: Annotated[int, Path(description='ID of the competition')],
) -> List[GetTeam]:
    """Get all teams in a specific competition."""
    manager = TeamsManager(db=_db, logger=_logger)
    return manager.get_by_competition_id(competition_id)


@router.post(
        path='/teams',
        summary='Add a new team to a competition.')
async def add_team_to_competition(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    team: AddTeam,
) -> GetTeam:
    """Add a new team."""
    manager = TeamsManager(db=_db, logger=_logger)
    item_id = manager.add_one(team, competition_id, commit=True)
    if item_id is None:
        raise ApiError('No data was inserted or updated.')
    item = manager.get_by_id(team_id=item_id)
    if item is None:
        raise ApiError('It was not possible to locate the new data.')
    return item


@router.get(
        path='/teams/{team_id}',  # noqa: FS003
        summary='Get a team of a competition')
async def get_team_by_id(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    team_id: Annotated[int, Path(description='ID of the team')],
) -> Union[GetTeam, Empty]:
    """Get a team by its ID."""
    manager = TeamsManager(db=_db, logger=_logger)
    item = manager.get_by_id(team_id=team_id, competition_id=competition_id)
    return Empty() if item is None else item


@router.put(
        path='/teams/{team_id}',  # noqa: FS003
        summary='Update a team of a competition')
async def update_team_by_id(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    team_id: Annotated[int, Path(description='ID of the team')],
    team: UpdateTeam,
) -> GetTeam:
    """Update the data of a team."""
    manager = TeamsManager(db=_db, logger=_logger)
    manager.update_by_id(
        team, team_id=team_id, competition_id=competition_id)
    item = manager.get_by_id(team_id, competition_id)
    if item is None:
        raise ApiError('No data was inserted or updated.')
    return item


@router.get(
        path='/teams/{team_id}/drivers',  # noqa: FS003
        summary='Get all the drivers in a team')
async def get_team_drivers_by_team_id(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    team_id: Annotated[int, Path(description='ID of the team')],
) -> List[GetDriver]:
    """Get all drivers in a specific team."""
    manager = DriversManager(db=_db, logger=_logger)
    return manager.get_by_team_id(team_id, competition_id)


@router.post(
        path='/teams/{team_id}/drivers',  # noqa: FS003
        summary='Add a new driver to a team')
async def add_team_driver(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    team_id: Annotated[int, Path(description='ID of the team')],
    driver: AddDriver,
) -> GetDriver:
    """Add a new driver in the team."""
    manager = DriversManager(db=_db, logger=_logger)
    item_id = manager.add_one(
        driver, competition_id=competition_id, team_id=team_id, commit=True)
    if item_id is None:
        raise ApiError('No data was inserted or updated.')
    item = manager.get_by_id(item_id)
    if item is None:
        raise ApiError('It was not possible to locate the new data.')
    return item


@router.get(
        path='/teams/{team_id}/drivers/{driver_id}',  # noqa: FS003
        summary='Get a driver of a team')
async def get_team_driver_by_id(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    team_id: Annotated[int, Path(description='ID of the team')],
    driver_id: Annotated[int, Path(description='ID of the driver')],
) -> Union[GetDriver, Empty]:
    """Get a driver by its ID."""
    manager = DriversManager(db=_db, logger=_logger)
    item = manager.get_by_id(
        driver_id, team_id=team_id, competition_id=competition_id)
    return Empty() if item is None else item


@router.put(
        path='/teams/{team_id}/drivers/{driver_id}',  # noqa: FS003
        summary='Update a driver of a team')
async def update_team_driver_by_id(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    team_id: Annotated[int, Path(description='ID of the team')],
    driver_id: Annotated[int, Path(description='ID of the driver')],
    driver: UpdateDriver,
) -> GetDriver:
    """Update the data of a driver."""
    manager = DriversManager(db=_db, logger=_logger)
    manager.update_by_id(
        driver, driver_id, team_id=team_id, competition_id=competition_id)
    item = manager.get_by_id(
        driver_id, team_id=team_id, competition_id=competition_id)
    if item is None:
        raise ApiError('No data was inserted or updated.')
    return item


@router.get(
        path='/drivers',
        summary='Get all the drivers (w/wo team) in a competition')
async def get_single_drivers_by_competition_id(
    competition_id: Annotated[int, Path(description='ID of the competition')],
) -> List[GetDriver]:
    """Get all drivers in a specific competition."""
    manager = DriversManager(db=_db, logger=_logger)
    return manager.get_by_competition_id(competition_id)


@router.post(
        path='/drivers',
        summary='Add a driver (without team) to a competition')
async def add_single_driver(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    driver: AddDriver,
) -> GetDriver:
    """Add a new driver without team."""
    manager = DriversManager(db=_db, logger=_logger)
    item_id = manager.add_one(
        driver, competition_id=competition_id, commit=True)
    if item_id is None:
        raise ApiError('No data was inserted or updated.')
    item = manager.get_by_id(item_id)
    if item is None:
        raise ApiError('It was not possible to locate the new data.')
    return item


@router.get(
        path='/drivers/{driver_id}',  # noqa: FS003
        summary='Get a driver (w/wo team)')
async def get_single_driver_by_id(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    driver_id: Annotated[int, Path(description='ID of the driver')],
) -> Union[GetDriver, Empty]:
    """Get a driver by its ID."""
    manager = DriversManager(db=_db, logger=_logger)
    item = manager.get_by_id(driver_id, competition_id=competition_id)
    return Empty() if item is None else item


@router.put(
        path='/drivers/{driver_id}',  # noqa: FS003
        summary='Update a driver (w/wo team) of a competition')
async def update_single_driver_by_id(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    driver_id: Annotated[int, Path(description='ID of the driver')],
    driver: UpdateDriver,
) -> GetDriver:
    """Update the data of a driver."""
    manager = DriversManager(db=_db, logger=_logger)
    manager.update_by_id(driver, driver_id, competition_id=competition_id)
    item = manager.get_by_id(driver_id, competition_id=competition_id)
    if item is None:
        raise ApiError('No data was inserted or updated.')
    return item

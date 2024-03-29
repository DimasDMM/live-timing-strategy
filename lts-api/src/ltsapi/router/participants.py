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
    UpdatePartialTimeDriver,
    UpdateTotalTimeDriver,
)
from ltsapi.models.responses import Empty
from ltsapi.router import _build_db_connection


router = APIRouter(
    prefix='/' + API_VERSION + '/c/{competition_id}',  # noqa
    tags=['Participants'])
_logger = _build_logger(__package__)


@router.get(
        path='/teams',
        summary='Get all teams in a competition')
async def get_teams_by_competition_id(
    competition_id: Annotated[int, Path(description='ID of the competition')],
) -> List[GetTeam]:
    """Get all teams in a specific competition."""
    db = _build_db_connection(_logger)
    with db:
        manager = TeamsManager(db=db, logger=_logger)
        return manager.get_by_competition_id(competition_id)


@router.post(
        path='/teams',
        summary='Add a new team to a competition.')
async def add_team_to_competition(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    team: AddTeam,
) -> GetTeam:
    """Add a new team."""
    db = _build_db_connection(_logger)
    with db:
        db.start_transaction()
        manager = TeamsManager(db=db, logger=_logger)
        try:
            item_id = manager.add_one(team, competition_id, commit=True)
        except ApiError as e:
            raise e
        except Exception:
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
    db = _build_db_connection(_logger)
    with db:
        manager = TeamsManager(db=db, logger=_logger)
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
    db = _build_db_connection(_logger)
    with db:
        db.start_transaction()
        manager = TeamsManager(db=db, logger=_logger)
        manager.update_by_id(
            team, team_id=team_id, competition_id=competition_id)
        item = manager.get_by_id(team_id, competition_id)
        if item is None:
            raise ApiError('No data was inserted or updated.')
        return item


@router.get(
        path='/teams/filter/code/{participant_code}',  # noqa
        summary='Get a team by its code')
async def get_team_by_code(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    participant_code: Annotated[str, Path(
        description='Code of the participant')],
) -> Union[GetTeam, Empty]:
    """Get a team by its code."""
    db = _build_db_connection(_logger)
    with db:
        db.start_transaction()
        manager = TeamsManager(db=db, logger=_logger)
        item = manager.get_by_code(
            participant_code=participant_code,
            competition_id=competition_id)
        return Empty() if item is None else item


@router.get(
        path='/teams/{team_id}/drivers',  # noqa: FS003
        summary='Get all the drivers in a team')
async def get_team_drivers_by_team_id(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    team_id: Annotated[int, Path(description='ID of the team')],
) -> List[GetDriver]:
    """Get all drivers in a specific team."""
    db = _build_db_connection(_logger)
    with db:
        manager = DriversManager(db=db, logger=_logger)
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
    db = _build_db_connection(_logger)
    with db:
        db.start_transaction()
        manager = DriversManager(db=db, logger=_logger)
        try:
            item_id = manager.add_one(
                driver,
                competition_id=competition_id,
                team_id=team_id,
                commit=True)
        except ApiError as e:
            raise e
        except Exception:
            raise ApiError('No data was inserted or updated.')
        item = manager.get_by_id(item_id)
        if item is None:
            raise ApiError('It was not possible to locate the new data.')
        return item


@router.get(
        path='/teams/{team_id}/drivers/filter/name/{driver_name}',  # noqa
        summary='Get a driver by its name in a team')
async def get_team_driver_by_driver_name(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    team_id: Annotated[int, Path(description='ID of the team')],
    driver_name: Annotated[str, Path(description='Name of the driver')],
) -> Union[GetDriver, Empty]:
    """Get a driver by its name in a team."""
    db = _build_db_connection(_logger)
    with db:
        db.start_transaction()
        manager = DriversManager(db=db, logger=_logger)
        item = manager.get_by_name(
            driver_name=driver_name,
            competition_id=competition_id,
            team_id=team_id)
        return Empty() if item is None else item


@router.get(
        path='/drivers',
        summary='Get all the drivers (w/wo team) in a competition')
async def get_all_drivers(
    competition_id: Annotated[int, Path(description='ID of the competition')],
) -> List[GetDriver]:
    """Get all drivers in a specific competition."""
    db = _build_db_connection(_logger)
    with db:
        manager = DriversManager(db=db, logger=_logger)
        return manager.get_by_competition_id(competition_id)


@router.post(
        path='/drivers',
        summary='Add a driver (without team) to a competition')
async def add_single_driver(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    driver: AddDriver,
) -> GetDriver:
    """Add a new driver without team."""
    db = _build_db_connection(_logger)
    with db:
        db.start_transaction()
        manager = DriversManager(db=db, logger=_logger)
        try:
            item_id = manager.add_one(
                driver, competition_id=competition_id, commit=True)
        except ApiError as e:
            raise e
        except Exception:
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
    db = _build_db_connection(_logger)
    with db:
        manager = DriversManager(db=db, logger=_logger)
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
    db = _build_db_connection(_logger)
    with db:
        db.start_transaction()
        manager = DriversManager(db=db, logger=_logger)
        manager.update_by_id(driver, driver_id, competition_id=competition_id)
        item = manager.get_by_id(driver_id, competition_id=competition_id)
        if item is None:
            raise ApiError('No data was inserted or updated.')
        return item


@router.put(
        path='/drivers/{driver_id}/partial_driving_time',  # noqa: FS003
        summary='Update the partial driving time of a driver in a competition')
async def update_driver_partial_driving_time(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    driver_id: Annotated[int, Path(description='ID of the driver')],
    time: UpdatePartialTimeDriver,
) -> GetDriver:
    """Update the partial driving time of a driver in a competition."""
    db = _build_db_connection(_logger)
    with db:
        db.start_transaction()
        manager = DriversManager(db=db, logger=_logger)
        manager.update_partial_driving_time_by_id(
            time, driver_id, competition_id=competition_id)
        item = manager.get_by_id(driver_id, competition_id=competition_id)
        if item is None:
            raise ApiError('No data was inserted or updated.')
        return item


@router.put(
        path='/drivers/{driver_id}/total_driving_time',  # noqa: FS003
        summary='Update the total driving time of a driver in a competition')
async def update_driver_total_driving_time(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    driver_id: Annotated[int, Path(description='ID of the driver')],
    time: UpdateTotalTimeDriver,
) -> GetDriver:
    """Update the total driving time of a driver in a competition."""
    db = _build_db_connection(_logger)
    with db:
        db.start_transaction()
        manager = DriversManager(db=db, logger=_logger)
        manager.update_total_driving_time_by_id(
            time, driver_id, competition_id=competition_id)
        item = manager.get_by_id(driver_id, competition_id=competition_id)
        if item is None:
            raise ApiError('No data was inserted or updated.')
        return item

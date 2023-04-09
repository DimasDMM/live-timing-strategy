from fastapi import APIRouter, Path
from typing import Annotated, List, Union

from ltsapi import API_VERSION, _build_logger
from ltsapi.exceptions import ApiError
from ltsapi.managers.participants import DriversManager, TeamsManager
from ltsapi.models.filters import CodeFilter, IdFilter, NameFilter
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


router = APIRouter(prefix=f'/{API_VERSION}/participants', tags=['Participants'])
_logger = _build_logger(__package__)
_db = _build_db_connection(_logger)


@router.post('/teams')
async def add_team(team: AddTeam) -> GetTeam:
    """Add a new team."""
    manager = TeamsManager(db=_db, logger=_logger)
    manager.add_one(team, commit=True)
    item = manager.get_by_code_and_competition(
        CodeFilter(code=team.code), IdFilter(id=team.competition_id))
    if item is None:
        raise ApiError('No data was inserted or updated.')
    return item


@router.get('/teams/{team_id}')  # noqa: FS003
async def get_team_by_id(
    team_id: Annotated[int, Path(title='The ID of the team')],
) -> Union[GetTeam, Empty]:
    """Get a team by its ID."""
    manager = TeamsManager(db=_db, logger=_logger)
    item = manager.get_by_id(IdFilter(id=team_id))
    return Empty() if item is None else item


@router.put('/teams/{team_id}')  # noqa: FS003
async def update_team_by_id(
    team_id: Annotated[int, Path(title='The ID of the team')],
    team: UpdateTeam,
) -> GetTeam:
    """Update the data of a team."""
    _validate_team_id(team_id, team)
    manager = TeamsManager(db=_db, logger=_logger)
    manager.update_by_id(team)
    item = manager.get_by_id(IdFilter(id=team_id))
    if item is None:
        raise ApiError('No data was inserted or updated.')
    return item


@router.get('/teams/filter/competition/{competition_id}')  # noqa: FS003
async def get_teams_by_competition_id(
    competition_id: Annotated[int, Path(title='The ID of the competition')],
) -> List[GetTeam]:
    """Get all teams in a specific competition."""
    manager = TeamsManager(db=_db, logger=_logger)
    return manager.get_by_competition_id(IdFilter(id=competition_id))


@router.post('/drivers')
async def add_driver(driver: AddDriver) -> GetDriver:
    """Add a new driver."""
    manager = DriversManager(db=_db, logger=_logger)
    manager.add_one(driver, commit=True)
    item = manager.get_by_name_and_competition(
        NameFilter(name=driver.name), IdFilter(id=driver.competition_id))
    if item is None:
        raise ApiError('No data was inserted or updated.')
    return item


@router.get('/drivers/{driver_id}')  # noqa: FS003
async def get_driver_by_id(
    driver_id: Annotated[int, Path(title='The ID of the driver')],
) -> Union[GetDriver, Empty]:
    """Get a driver by its ID."""
    manager = DriversManager(db=_db, logger=_logger)
    item = manager.get_by_id(IdFilter(id=driver_id))
    return Empty() if item is None else item


@router.put('/drivers/{driver_id}')  # noqa: FS003
async def update_driver_by_id(
    driver_id: Annotated[int, Path(title='The ID of the driver')],
    driver: UpdateDriver,
) -> GetDriver:
    """Update the data of a driver."""
    _validate_driver_id(driver_id, driver)
    manager = DriversManager(db=_db, logger=_logger)
    manager.update_by_id(driver)
    item = manager.get_by_id(IdFilter(id=driver_id))
    if item is None:
        raise ApiError('No data was inserted or updated.')
    return item


@router.get('/drivers/filter/competition/{competition_id}')  # noqa: FS003
async def get_drivers_by_competition_id(
    competition_id: Annotated[int, Path(title='The ID of the competition')],
) -> List[GetDriver]:
    """Get all drivers in a specific competition."""
    manager = DriversManager(db=_db, logger=_logger)
    return manager.get_by_competition_id(IdFilter(id=competition_id))


@router.get('/drivers/filter/team/{team_id}')  # noqa: FS003
async def get_drivers_by_team_id(
    team_id: Annotated[int, Path(title='The ID of the team')],
) -> List[GetDriver]:
    """Get all drivers in a specific team."""
    manager = DriversManager(db=_db, logger=_logger)
    return manager.get_by_team_id(IdFilter(id=team_id))


def _validate_team_id(team_id: int, team: UpdateTeam) -> None:
    """Validate that the given ID coincides with the team data."""
    if team_id != team.id:
        raise ApiError(
            message=f'The IDs does not coincide ({team_id} != {team.id}).',
            status_code=400,
        )


def _validate_driver_id(driver_id: int, driver: UpdateDriver) -> None:
    """Validate that the given ID coincides with the driver data."""
    if driver_id != driver.id:
        raise ApiError(
            message=f'The IDs does not coincide ({driver_id} != {driver.id}).',
            status_code=400,
        )

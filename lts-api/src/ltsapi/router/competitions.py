from fastapi import APIRouter, Path
from typing import Annotated, List, Union

from ltsapi import API_VERSION, _build_logger
from ltsapi.exceptions import ApiError
from ltsapi.managers.competitions import (
    CompetitionsIndexManager,
    TracksManager,
)
from ltsapi.models.competitions import (
    AddCompetition,
    AddTrack,
    GetCompetition,
    GetTrack,
    UpdateTrack,
)
from ltsapi.models.responses import Empty
from ltsapi.router import _build_db_connection


router = APIRouter(
    prefix=f'/{API_VERSION}', tags=['Competitions (generic)'])
_logger = _build_logger(__package__)
_db = _build_db_connection(_logger)


@router.get(
        path='/competitions',
        summary='Get all the competitions')
async def get_all_competitions() -> List[GetCompetition]:
    """Get all competitions in the database."""
    manager = CompetitionsIndexManager(db=_db, logger=_logger)
    return manager.get_all()


@router.post(
        path='/competitions',
        summary='Add a new competition')
async def add_competition(competition: AddCompetition) -> GetCompetition:
    """Add a new competition."""
    manager = CompetitionsIndexManager(db=_db, logger=_logger)
    item_id = manager.add_one(competition, commit=True)
    if item_id is None:
        raise ApiError('No data was inserted or updated.')
    item = manager.get_by_id(item_id)
    if item is None:
        raise ApiError('It was not possible to locate the new data.')
    return item


@router.get(
        path='/competitions/{competition_id}',  # noqa: FS003
        summary='Get a competition')
async def get_competition_by_id(
    competition_id: Annotated[int, Path(description='ID of the competition')],
) -> Union[GetCompetition, Empty]:
    """Get a competition from the database by its ID."""
    manager = CompetitionsIndexManager(db=_db, logger=_logger)
    item = manager.get_by_id(competition_id)
    return Empty() if item is None else item


@router.get(
        path='/competitions/filter/code/{competition_code}',  # noqa: FS003
        summary='Get a competition (by its code)')
async def get_competition_by_code(
    competition_code: Annotated[str, Path(
        description='Code of the competition')],
) -> Union[GetCompetition, Empty]:
    """Get a competition from the database by its code."""
    manager = CompetitionsIndexManager(db=_db, logger=_logger)
    item = manager.get_by_code(competition_code)
    return Empty() if item is None else item


@router.get(
        path='/tracks',
        summary='Get all the tracks')
async def get_all_tracks() -> List[GetTrack]:
    """Get all tracks in the database."""
    manager = TracksManager(db=_db, logger=_logger)
    return manager.get_all()


@router.post(
        path='/tracks',
        summary='Add a new track')
async def add_track(track: AddTrack) -> GetTrack:
    """Add a new track."""
    manager = TracksManager(db=_db, logger=_logger)
    item_id = manager.add_one(track, commit=True)
    if item_id is None:
        raise ApiError('No data was inserted or updated.')
    item = manager.get_by_id(item_id)
    if item is None:
        raise ApiError('It was not possible to locate the new data.')
    return item


@router.put(
        path='/tracks/{track_id}',  # noqa: FS003
        summary='Update a track of a competition')
async def update_track_by_id(
    track_id: Annotated[int, Path(description='ID of the track')],
    track: UpdateTrack,
) -> GetTrack:
    """Update the data of a track."""
    manager = TracksManager(db=_db, logger=_logger)
    manager.update_by_id(track, track_id)
    item = manager.get_by_id(track_id)
    if item is None:
        raise ApiError('No data was inserted or updated.')
    return item

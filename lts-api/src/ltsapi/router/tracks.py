from fastapi import APIRouter, Path
from typing import Annotated, List

from ltsapi import API_VERSION, _build_logger
from ltsapi.exceptions import ApiError
from ltsapi.managers.tracks import TracksManager
from ltsapi.models.tracks import (
    AddTrack,
    GetTrack,
    UpdateTrack,
)
from ltsapi.router import _build_db_connection


router = APIRouter(
    prefix=f'/{API_VERSION}', tags=['Tracks'])
_logger = _build_logger(__package__)


@router.get(
        path='/tracks',
        summary='Get all the tracks')
async def get_all_tracks() -> List[GetTrack]:
    """Get all tracks in the database."""
    db = _build_db_connection(_logger)
    with db:
        manager = TracksManager(db=db, logger=_logger)
        return manager.get_all()


@router.post(
        path='/tracks',
        summary='Add a new track')
async def add_track(track: AddTrack) -> GetTrack:
    """Add a new track."""
    db = _build_db_connection(_logger)
    with db:
        db.start_transaction()
        manager = TracksManager(db=db, logger=_logger)
        try:
            item_id = manager.add_one(track, commit=True)
        except ApiError as e:
            raise e
        except Exception:
            raise ApiError('No data was inserted or updated.')
        item = manager.get_by_id(item_id)
        if item is None:
            raise ApiError('It was not possible to locate the new data.')
        return item


@router.put(
        path='/tracks/{track_id}',  # noqa: FS003
        summary='Update a track')
async def update_track_by_id(
    track_id: Annotated[int, Path(description='ID of the track')],
    track: UpdateTrack,
) -> GetTrack:
    """Update the data of a track."""
    db = _build_db_connection(_logger)
    with db:
        db.start_transaction()
        manager = TracksManager(db=db, logger=_logger)
        manager.update_by_id(track, track_id)
        item = manager.get_by_id(track_id)
        if item is None:
            raise ApiError('No data was inserted or updated.')
        return item

from fastapi import APIRouter, Path
from typing import Annotated, List, Union

from ltsapi import API_VERSION, _build_logger
from ltsapi.exceptions import ApiError
from ltsapi.managers.parsers import ParsersSettingsManager
from ltsapi.managers.tracks import TracksManager
from ltsapi.models.parsers import (
    AddParserSetting,
    GetParserSetting,
    UpdateParserSetting,
)
from ltsapi.models.tracks import (
    AddTrack,
    GetTrack,
    UpdateTrack,
)
from ltsapi.models.responses import Empty
from ltsapi.router import _build_db_connection


router = APIRouter(
    prefix=f'/{API_VERSION}', tags=['Misc.'])
_logger = _build_logger(__package__)


@router.get(
        path='/competitions/{competition_id}/parsers/settings',  # noqa: FS003
        summary='Get parsers settings')
async def get_parsers_settings(
    competition_id: Annotated[int, Path(description='ID of the competition')],
) -> List[GetParserSetting]:
    """Get parsers settings."""
    db = _build_db_connection(_logger)
    with db:
        manager = ParsersSettingsManager(db=db, logger=_logger)
        return manager.get_by_competition(competition_id)


@router.post(
        path='/competitions/{competition_id}/parsers/settings',  # noqa: FS003
        summary='Add a new parser setting')
async def add_parser_setting(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    setting: AddParserSetting,
) -> GetParserSetting:
    """Add a new parser setting."""
    db = _build_db_connection(_logger)
    with db:
        manager = ParsersSettingsManager(db=db, logger=_logger)
        item_id = manager.add_one(
            setting, competition_id=competition_id, commit=True)
        if item_id is None:
            raise ApiError('No data was inserted or updated.')
        item = manager.get_by_name(setting.name, competition_id=competition_id)
        if item is None:
            raise ApiError('It was not possible to locate the new data.')
        return item


@router.delete(
        path='/competitions/{competition_id}/parsers/settings',  # noqa: FS003
        summary='Delete all the parsers settings of a competition')
async def delete_parsers_settings(
    competition_id: Annotated[int, Path(description='ID of the competition')],
) -> Empty:
    """Delete all the parsers settings of a competition."""
    db = _build_db_connection(_logger)
    with db:
        manager = ParsersSettingsManager(db=db, logger=_logger)
        manager.delete_by_competition(competition_id, commit=True)
        return Empty()


@router.get(
        path='/competitions/{competition_id}/parsers/settings/{setting_name}',  # noqa
        summary='Get a specific parser setting')
async def get_single_parser_setting(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    setting_name: Annotated[str, Path(description='Name of the setting')],
) -> Union[GetParserSetting, Empty]:
    """Get a specific parser setting."""
    db = _build_db_connection(_logger)
    with db:
        manager = ParsersSettingsManager(db=db, logger=_logger)
        item = manager.get_by_name(
            competition_id=competition_id, setting_name=setting_name)
        return Empty() if item is None else item


@router.put(
        path='/competitions/{competition_id}/parsers/settings/{setting_name}',  # noqa
        summary='Update the value of a parser setting')
async def update_parser_setting(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    setting_name: Annotated[str, Path(description='Name of the setting')],
    setting: UpdateParserSetting,
) -> GetParserSetting:
    """Update the value of a parser setting."""
    db = _build_db_connection(_logger)
    with db:
        manager = ParsersSettingsManager(db=db, logger=_logger)
        manager.update_by_name(
            setting, setting_name=setting_name, competition_id=competition_id)
        item = manager.get_by_name(
            setting_name=setting_name, competition_id=competition_id)
        if item is None:
            raise ApiError('No data was inserted or updated.')
        return item


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
        manager = TracksManager(db=db, logger=_logger)
        item_id = manager.add_one(track, commit=True)
        if item_id is None:
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
        manager = TracksManager(db=db, logger=_logger)
        manager.update_by_id(track, track_id)
        item = manager.get_by_id(track_id)
        if item is None:
            raise ApiError('No data was inserted or updated.')
        return item

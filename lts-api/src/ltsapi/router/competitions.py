from fastapi import APIRouter, Path
from typing import Annotated, List, Union

from ltsapi import API_VERSION, _build_logger
from ltsapi.exceptions import ApiError
from ltsapi.managers.competitions import (
    CompetitionsIndexManager,
    CMetadataManager,
    CSettingsManager,
)
from ltsapi.models.competitions import (
    AddCompetition,
    GetCompetition,
    GetCompetitionMetadata,
    GetCompetitionSettings,
    UpdateCompetitionMetadata,
    UpdateCompetitionSettings,
)
from ltsapi.models.responses import Empty
from ltsapi.router import _build_db_connection


router = APIRouter(
    prefix=f'/{API_VERSION}', tags=['Competitions (base)'])
_logger = _build_logger(__package__)


@router.get(
        path='/competitions',
        summary='Get all the competitions')
async def get_all_competitions() -> List[GetCompetition]:
    """Get all competitions in the database."""
    db = _build_db_connection(_logger)
    with db:
        manager = CompetitionsIndexManager(db=db, logger=_logger)
        return manager.get_all()


@router.post(
        path='/competitions',
        summary='Add a new competition')
async def add_competition(competition: AddCompetition) -> GetCompetition:
    """Add a new competition."""
    db = _build_db_connection(_logger)
    with db:
        db.start_transaction()
        manager = CompetitionsIndexManager(db=db, logger=_logger)
        try:
            item_id = manager.add_one(competition, commit=True)
        except ApiError as e:
            raise e
        except Exception:
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
    db = _build_db_connection(_logger)
    with db:
        manager = CompetitionsIndexManager(db=db, logger=_logger)
        item = manager.get_by_id(competition_id)
        return Empty() if item is None else item


@router.get(
        path='/competitions/{competition_id}/metadata',  # noqa: FS003
        summary='Get the current metadata of a competition')
async def get_current_competition_metadata(
    competition_id: Annotated[int, Path(description='ID of the competition')],
) -> Union[GetCompetitionMetadata, Empty]:
    """Get the current metadata of a competition."""
    db = _build_db_connection(_logger)
    with db:
        manager = CMetadataManager(db=db, logger=_logger)
        item = manager.get_current_by_id(competition_id)
        return Empty() if item is None else item


@router.put(
        path='/competitions/{competition_id}/metadata',  # noqa: FS003
        summary='Update the metadata of a competition')
async def update_competition_metadata(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    metadata: UpdateCompetitionMetadata,
) -> GetCompetitionMetadata:
    """Update the metadata of a competition."""
    db = _build_db_connection(_logger)
    with db:
        db.start_transaction()
        manager = CMetadataManager(db=db, logger=_logger)
        manager.update_by_id(metadata, competition_id=competition_id)
        item = manager.get_current_by_id(competition_id)
        if item is None:
            raise ApiError('No data was inserted or updated.')
        return item


@router.get(
        path='/competitions/{competition_id}/metadata/history',  # noqa: FS003
        summary='Get the history metadata of a competition')
async def get_history_competition_metadata(
    competition_id: Annotated[int, Path(description='ID of the competition')],
) -> List[GetCompetitionMetadata]:
    """Get the history metadata of a competition."""
    db = _build_db_connection(_logger)
    with db:
        manager = CMetadataManager(db=db, logger=_logger)
        return manager.get_history_by_id(competition_id)


@router.get(
        path='/competitions/{competition_id}/settings',  # noqa: FS003
        summary='Get the settings of a competition')
async def get_competition_settings(
    competition_id: Annotated[int, Path(description='ID of the competition')],
) -> Union[GetCompetitionSettings, Empty]:
    """Get the settings of a competition."""
    db = _build_db_connection(_logger)
    with db:
        manager = CSettingsManager(db=db, logger=_logger)
        item = manager.get_by_id(competition_id)
        return Empty() if item is None else item


@router.put(
        path='/competitions/{competition_id}/settings',  # noqa: FS003
        summary='Update the settings of a competition')
async def update_competition_settings(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    settings: UpdateCompetitionSettings,
) -> GetCompetitionSettings:
    """Update the settings of a competition."""
    db = _build_db_connection(_logger)
    with db:
        db.start_transaction()
        manager = CSettingsManager(db=db, logger=_logger)
        manager.update_by_id(settings, competition_id=competition_id)
        item = manager.get_by_id(competition_id)
        if item is None:
            raise ApiError('No data was inserted or updated.')
        return item


@router.get(
        path='/competitions/filter/code/{competition_code}',  # noqa: FS003
        summary='Get a competition (by its code)')
async def get_competition_by_code(
    competition_code: Annotated[str, Path(
        description='Code of the competition')],
) -> Union[GetCompetition, Empty]:
    """Get a competition from the database by its code."""
    db = _build_db_connection(_logger)
    with db:
        manager = CompetitionsIndexManager(db=db, logger=_logger)
        item = manager.get_by_code(competition_code)
        return Empty() if item is None else item

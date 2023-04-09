from fastapi import APIRouter, Path
from typing import Annotated, List, Union

from ltsapi import API_VERSION, _build_logger
from ltsapi.exceptions import ApiError
from ltsapi.managers.competitions import CompetitionManager
from ltsapi.models.filters import CodeFilter, IdFilter
from ltsapi.models.competitions import AddCompetition, GetCompetition
from ltsapi.models.responses import Empty
from ltsapi.router import _build_db_connection


router = APIRouter(prefix=f'/{API_VERSION}/competitions', tags=['Competitions'])
_logger = _build_logger(__package__)
_db = _build_db_connection(_logger)


@router.get('/')
async def get_all_competitions() -> List[GetCompetition]:
    """Get all competitions in the database."""
    manager = CompetitionManager(db=_db, logger=_logger)
    return manager.get_all()


@router.post('/')
async def add_competition(competition: AddCompetition) -> GetCompetition:
    """Add a new competition."""
    manager = CompetitionManager(db=_db, logger=_logger)
    manager.add_one(competition, commit=True)
    item = manager.get_by_code(CodeFilter(code=competition.code))
    if item is None:
        raise ApiError('No data was inserted or updated.')
    return item


@router.get('/{id}')  # noqa: FS003
async def get_competition_by_id(
    id: Annotated[int, Path(title='The ID of the competition')],
) -> Union[GetCompetition, Empty]:
    """Get a competition from the database by its ID."""
    manager = CompetitionManager(db=_db, logger=_logger)
    item = manager.get_by_id(IdFilter(id=id))
    return Empty() if item is None else item


@router.get('/filter/code/{code}')  # noqa: FS003
async def get_competition_by_code(
    code: Annotated[str, Path(title='The code of the competition')],
) -> Union[GetCompetition, Empty]:
    """Get a competition from the database by its code."""
    manager = CompetitionManager(db=_db, logger=_logger)
    item = manager.get_by_code(CodeFilter(code=code))
    return Empty() if item is None else item

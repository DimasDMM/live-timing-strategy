from fastapi import APIRouter, Path
from typing import Annotated, List, Union

from ltsapi import API_VERSION, _build_logger
from ltsapi.exceptions import ApiError
from ltsapi.managers.strategy import (
    StrategyPitsKartsManager,
    StrategyPitsStatsManager,
)
from ltsapi.models.responses import Empty
from ltsapi.models.strategy import (
    AddStrategyPitsKarts,
    GetStrategyPitsKarts,
    AddStrategyPitsStats,
    GetStrategyPitsStats,
)
from ltsapi.router import _build_db_connection


router = APIRouter(
    prefix='/' + API_VERSION + '/c/{competition_id}',  # noqa
    tags=['Strategy'])
_logger = _build_logger(__package__)


@router.post(
        path='/strategy/pits/karts',
        summary='Add a strategy pit karts')
async def add_strategy_pits_karts(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    strategy: List[AddStrategyPitsKarts],
) -> List[GetStrategyPitsKarts]:
    """Add a strategy pit karts."""
    db = _build_db_connection(_logger)
    with db:
        db.start_transaction()
        manager = StrategyPitsKartsManager(db=db, logger=_logger)
        try:
            _ = manager.add_many(strategy, commit=True)
        except ApiError as e:
            raise e
        except Exception:
            raise ApiError('No data was inserted or updated.')

        if len(strategy) == 0:
            raise ApiError('It was not possible to locate the new data.')

        pit_in_id = strategy[0].pit_in_id  # type: ignore
        items = manager.get_strategy_by_pit_in(competition_id, pit_in_id)
        return items


@router.get(
        path='/strategy/pits/karts/{pit_in_id}',  # noqa: FS003
        summary='Get a strategy pit karts')
async def get_strategy_pits_karts_by_pit_in(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    pit_in_id: Annotated[int, Path(description='ID of the pit-in')],
) -> List[GetStrategyPitsKarts]:
    """Get the data of a strategy pit karts."""
    db = _build_db_connection(_logger)
    with db:
        db.start_transaction()
        manager = StrategyPitsKartsManager(db=db, logger=_logger)
        items = manager.get_strategy_by_pit_in(competition_id, pit_in_id)
        return items


@router.post(
        path='/strategy/pits/stats',
        summary='Add a strategy pit stats')
async def add_strategy_pits_stats(
    competition_id: Annotated[int, Path(description='ID of the competition')],  # noqa: U100, E501
    strategy: AddStrategyPitsStats,
) -> GetStrategyPitsStats:
    """Add a strategy pit stats."""
    db = _build_db_connection(_logger)
    with db:
        db.start_transaction()
        manager = StrategyPitsStatsManager(db=db, logger=_logger)
        try:
            _ = manager.add_one(strategy, commit=True)
        except ApiError as e:
            raise e
        except Exception:
            raise ApiError('No data was inserted or updated.')
        item = manager.get_last_by_pit_in(strategy.pit_in_id)
        if item is None:
            raise ApiError('It was not possible to locate the new data.')
        return item


@router.get(
        path='/strategy/pits/stats/{pit_in_id}',  # noqa: FS003
        summary='Get a strategy pit stats')
async def get_strategy_pits_stats_by_pit_in(
    competition_id: Annotated[int, Path(description='ID of the competition')],  # noqa: U100, E501
    pit_in_id: Annotated[int, Path(description='ID of the pit-in')],
) -> Union[GetStrategyPitsStats, Empty]:
    """Get the data of a strategy pit stats."""
    db = _build_db_connection(_logger)
    with db:
        db.start_transaction()
        manager = StrategyPitsStatsManager(db=db, logger=_logger)
        item = manager.get_last_by_pit_in(pit_in_id)
        if item is None:
            return Empty()
        return item

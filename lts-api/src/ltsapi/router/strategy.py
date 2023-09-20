from fastapi import APIRouter, Path
from typing import Annotated, Union

from ltsapi import API_VERSION, _build_logger
from ltsapi.exceptions import ApiError
from ltsapi.managers.strategy import (
    StrategyPitsStatsManager,
)
from ltsapi.models.responses import Empty
from ltsapi.models.strategy import (
    AddStrategyPitsStats,
    GetStrategyPitsStats,
)
from ltsapi.router import _build_db_connection


router = APIRouter(
    prefix=f'/{API_VERSION}', tags=['Strategy'])
_logger = _build_logger(__package__)


@router.post(
        path='/strategy/pits/stats',
        summary='Add a strategy pit stats')
async def add_strategy_pits_stats(
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

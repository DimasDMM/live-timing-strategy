from logging import Logger
from typing import Optional

from ltsapi.db import DBContext
from ltsapi.exceptions import ApiError
from ltsapi.managers.utils.statements import (
    insert_model,
    fetchone_model,
)
from ltsapi.models.strategy import (
    AddStrategyPitsStats,
    GetStrategyPitsStats,
)


class StrategyPitsStatsManager:
    """Manage the strategy pit stats."""

    BASE_QUERY = '''
        SELECT
            sps.`id` AS sps_id,
            sps.`pit_in_id` AS sps_pit_in_id,
            sps.`best_time` AS sps_best_time,
            sps.`avg_time` AS sps_avg_time,
            sps.`insert_date` AS sps_insert_date,
            sps.`update_date` AS sps_update_date
        FROM strategy_pits_stats AS sps'''
    TABLE_NAME = 'strategy_pits_stats'

    def __init__(self, db: DBContext, logger: Logger) -> None:
        """Construct."""
        self._db = db
        self._logger = logger

    def get_last_by_pit_in(
            self,
            pit_in_id: int) -> Optional[GetStrategyPitsStats]:
        """
        Retrieve a strategy pit stats by its ID.

        This method only returns the last computed item for the given pit-in.

        Params:
            pit_in_id (int): ID of the pit-in.

        Returns:
            GetStrategyPitsStats | None: If the item exists, returns
                its instance.
        """
        query = f'''
            {self.BASE_QUERY}
            WHERE sps.`pit_in_id` = %s
            ORDER BY sps.`id` DESC LIMIT 1
            '''
        model: Optional[GetStrategyPitsStats] = fetchone_model(  # type: ignore
            self._db, self._raw_to_item, query, params=(pit_in_id,))
        return model

    def add_one(self, item: AddStrategyPitsStats, commit: bool = True) -> int:
        """
        Add a new strategy pit stats.

        Params:
            item (AddStrategyPitsStats): Data of the strategy pit stats.
            commit (bool): Commit transaction.

        Returns:
            int: ID of inserted model.
        """
        item_id = insert_model(
            self._db, self.TABLE_NAME, item.dict(), commit=commit)
        if item_id is None:
            raise ApiError('No data was inserted or updated.')
        return item_id

    def _raw_to_item(self, row: dict) -> GetStrategyPitsStats:
        """Build an instance of GetStrategyPitsStats."""
        return GetStrategyPitsStats(
            id=row['sps_id'],
            pit_in_id=row['sps_pit_in_id'],
            best_time=row['sps_best_time'],
            avg_time=row['sps_avg_time'],
            insert_date=row['sps_insert_date'],
            update_date=row['sps_update_date'],
        )

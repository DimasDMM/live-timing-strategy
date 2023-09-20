from logging import Logger
from typing import List, Optional

from ltsapi.db import DBContext
from ltsapi.exceptions import ApiError
from ltsapi.managers.utils.statements import (
    insert_model,
    fetchmany_models,
    fetchone_model,
)
from ltsapi.models.strategy import (
    AddStrategyPitsKarts,
    GetStrategyPitsKarts,
    AddStrategyPitsStats,
    GetStrategyPitsStats,
)


class StrategyPitsKartsManager:
    """Manage the strategy pits karts."""

    TABLE_NAME = 'strategy_pits_karts'

    def __init__(self, db: DBContext, logger: Logger) -> None:
        """Construct."""
        self._db = db
        self._logger = logger

    def get_last_by_pit_in(
            self,
            pit_in_id: int) -> Optional[GetStrategyPitsKarts]:
        """
        Retrieve a strategy pits karts by its ID.

        This method only returns the last computed item for the given pit-in.

        Params:
            pit_in_id (int): ID of the pit-in.

        Returns:
            List[GetStrategyPitsKarts]: If the item exists, returns
                its instance.
        """
        query = f'''
        WITH spk AS (
            SELECT
                ROW_NUMBER() OVER (PARTITION BY pit_in_id, step, kart_status ORDER BY id DESC) AS rn,
                spk.`id` AS spk_id,
                spk.`competition_id` AS spk_competition_id,
                spk.`pit_in_id` AS spk_pit_in_id,
                spk.`step` AS spk_step,
                spk.`kart_status` AS spk_kart_status,
                spk.`probability` AS spk_probability,
                spk.`insert_date` AS spk_insert_date,
                spk.`update_date` AS spk_update_date
            FROM {self.TABLE_NAME} AS spk
            WHERE spk.`pit_in_id` = %s
        )
        SELECT *
        FROM spk
        WHERE rn = 1
        ORDER BY spk_id ASC
        '''
        models: List[GetStrategyPitsKarts] = fetchmany_models(  # type: ignore
            self._db, self._raw_to_item, query, params=(pit_in_id,))
        return models

    def add_many(
            self,
            items: List[AddStrategyPitsKarts],
            commit: bool = True) -> List[int]:
        """
        Add a new strategy pits karts.

        Params:
            items (List[AddStrategyPitsKarts]): Data of the strategy pits karts.
            commit (bool): Commit transaction.

        Returns:
            List[int]: IDs of the inserted models.
        """
        item_ids: List[int] = []
        for item in items:
            item_id = insert_model(
                self._db, self.TABLE_NAME, item.dict(), commit=False)
            if item_id is None:
                raise ApiError('No data was inserted or updated.')
            item_ids.append(item_id)

        if len(item_ids) == 0:
            raise ApiError('No data was inserted or updated.')

        if commit:
            self._db.commit()

        return item_ids

    def _raw_to_item(self, row: dict) -> GetStrategyPitsKarts:
        """Build an instance of GetStrategyPitsKarts."""
        return GetStrategyPitsKarts(
            id=row['spk_id'],
            competition_id=row['spk_competition_id'],
            pit_in_id=row['spk_pit_in_id'],
            step=row['spk_step'],
            kart_status=row['spk_kart_status'],
            probability=row['spk_probability'],
            insert_date=row['spk_insert_date'],
            update_date=row['spk_update_date'],
        )


class StrategyPitsStatsManager:
    """Manage the strategy pits stats."""

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
        Retrieve a strategy pits stats by its ID.

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
        Add a new strategy pits stats.

        Params:
            item (AddStrategyPitsStats): Data of the strategy pits stats.
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

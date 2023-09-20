import pytest

from ltsapi.db import DBContext
from ltsapi.models.strategy import (
    AddStrategyPitsStats,
)
from ltsapi.managers.strategy import (
    StrategyPitsStatsManager,
)
from tests.helpers import DatabaseTest
from tests.mocks.logging import FakeLogger


class TestStrategyPitsStatsManager(DatabaseTest):
    """Test class ltsapi.managers.tracks.StrategyPitsStatsManager."""

    EXCLUDE = {
        'insert_date': True,
        'update_date': True,
    }

    @pytest.mark.parametrize(
        'pit_in_id, expected_item',
        [
            (
                3,  # pit_in_id
                {
                    'id': 1,
                    'pit_in_id': 3,
                    'best_time': 59500,
                    'avg_time': 59800,
                },
            ),
        ])
    def test_get_last_by_pit_in(
            self,
            pit_in_id: int,
            expected_item: dict,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method get_last_by_pit_in."""
        manager = StrategyPitsStatsManager(db=db_context, logger=fake_logger)

        db_item = manager.get_last_by_pit_in(pit_in_id)
        assert db_item is not None

        dict_item = db_item.dict(exclude=self.EXCLUDE)
        assert dict_item == expected_item

    @pytest.mark.parametrize(
        'model, expected_item',
        [
            (
                AddStrategyPitsStats(
                    pit_in_id=3,
                    best_time=59500,
                    avg_time=59800,
                ),
                {
                    'id': None,
                    'pit_in_id': 3,
                    'best_time': 59500,
                    'avg_time': 59800,
                },
            ),
        ])
    def test_add_one(
            self,
            model: AddStrategyPitsStats,
            expected_item: dict,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method add_one."""
        manager = StrategyPitsStatsManager(db=db_context, logger=fake_logger)
        item_id = manager.add_one(model, commit=True)

        expected_item['id'] = item_id
        db_item = manager.get_last_by_pit_in(model.pit_in_id)
        assert db_item is not None, f'>> ID : {item_id}'

        dict_item = db_item.dict(exclude=self.EXCLUDE)
        assert dict_item == expected_item

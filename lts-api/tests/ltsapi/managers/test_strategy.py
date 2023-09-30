import pytest
from typing import List

from ltsapi.db import DBContext
from ltsapi.models.enum import KartStatus
from ltsapi.models.strategy import (
    AddStrategyPitsKarts,
    AddStrategyPitsStats,
)
from ltsapi.managers.strategy import (
    StrategyPitsKartsManager,
    StrategyPitsStatsManager,
)
from tests.helpers import DatabaseTest
from tests.mocks.logging import FakeLogger


class TestStrategyPitsKartsManager(DatabaseTest):
    """Test class ltsapi.managers.tracks.StrategyPitsKartsManager."""

    EXCLUDE = {
        'insert_date': True,
        'update_date': True,
    }

    @pytest.mark.parametrize(
        'competition_id, pit_in_id, expected_items',
        [
            (
                2,  # competition_id
                3,  # pit_in_id
                [
                    {
                        'id': 13,
                        'pit_in_id': 3,
                        'competition_id': 2,
                        'step': 1,
                        'kart_status': KartStatus.GOOD,
                        'probability': 75.,
                    },
                    {
                        'id': 14,
                        'pit_in_id': 3,
                        'competition_id': 2,
                        'step': 1,
                        'kart_status': KartStatus.MEDIUM,
                        'probability': 5.,
                    },
                    {
                        'id': 15,
                        'pit_in_id': 3,
                        'competition_id': 2,
                        'step': 1,
                        'kart_status': KartStatus.BAD,
                        'probability': 20.,
                    },
                    {
                        'id': 16,
                        'pit_in_id': 3,
                        'competition_id': 2,
                        'step': 1,
                        'kart_status': KartStatus.UNKNOWN,
                        'probability': 0.,
                    },
                    {
                        'id': 17,
                        'pit_in_id': 3,
                        'competition_id': 2,
                        'step': 2,
                        'kart_status': KartStatus.GOOD,
                        'probability': 65.,
                    },
                    {
                        'id': 18,
                        'pit_in_id': 3,
                        'competition_id': 2,
                        'step': 2,
                        'kart_status': KartStatus.MEDIUM,
                        'probability': 3.,
                    },
                    {
                        'id': 19,
                        'pit_in_id': 3,
                        'competition_id': 2,
                        'step': 2,
                        'kart_status': KartStatus.BAD,
                        'probability': 12.,
                    },
                    {
                        'id': 20,
                        'pit_in_id': 3,
                        'competition_id': 2,
                        'step': 2,
                        'kart_status': KartStatus.UNKNOWN,
                        'probability': 20.,
                    },
                    {
                        'id': 21,
                        'pit_in_id': 3,
                        'competition_id': 2,
                        'step': 3,
                        'kart_status': KartStatus.GOOD,
                        'probability': 63.,
                    },
                    {
                        'id': 22,
                        'pit_in_id': 3,
                        'competition_id': 2,
                        'step': 3,
                        'kart_status': KartStatus.MEDIUM,
                        'probability': 2.,
                    },
                    {
                        'id': 23,
                        'pit_in_id': 3,
                        'competition_id': 2,
                        'step': 3,
                        'kart_status': KartStatus.BAD,
                        'probability': 10.,
                    },
                    {
                        'id': 24,
                        'pit_in_id': 3,
                        'competition_id': 2,
                        'step': 3,
                        'kart_status': KartStatus.UNKNOWN,
                        'probability': 30.,
                    },
                ],
            ),
        ])
    def test_get_strategy_by_pit_in(
            self,
            competition_id: int,
            pit_in_id: int,
            expected_items: list,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method get_strategy_by_pit_in."""
        manager = StrategyPitsKartsManager(db=db_context, logger=fake_logger)
        db_items = manager.get_strategy_by_pit_in(competition_id, pit_in_id)
        dict_items = [x.model_dump(exclude=self.EXCLUDE) for x in db_items]
        assert dict_items == expected_items

    @pytest.mark.parametrize(
        'competition_id, pit_in_id, models, expected_items',
        [
            (
                3,  # competition_id
                4,  # pit_in_id
                [
                    AddStrategyPitsKarts(
                        pit_in_id=4,
                        competition_id=3,
                        step=1,
                        kart_status=KartStatus.GOOD,
                        probability=20.,
                    ),
                    AddStrategyPitsKarts(
                        pit_in_id=4,
                        competition_id=3,
                        step=1,
                        kart_status=KartStatus.MEDIUM,
                        probability=30.,
                    ),
                    AddStrategyPitsKarts(
                        pit_in_id=4,
                        competition_id=3,
                        step=1,
                        kart_status=KartStatus.BAD,
                        probability=40.,
                    ),
                    AddStrategyPitsKarts(
                        pit_in_id=4,
                        competition_id=3,
                        step=1,
                        kart_status=KartStatus.UNKNOWN,
                        probability=10.,
                    ),
                ],
                [
                    {
                        'id': None,
                        'pit_in_id': 4,
                        'competition_id': 3,
                        'step': 1,
                        'kart_status': KartStatus.GOOD,
                        'probability': 20.,
                    },
                    {
                        'id': None,
                        'pit_in_id': 4,
                        'competition_id': 3,
                        'step': 1,
                        'kart_status': KartStatus.MEDIUM,
                        'probability': 30.,
                    },
                    {
                        'id': None,
                        'pit_in_id': 4,
                        'competition_id': 3,
                        'step': 1,
                        'kart_status': KartStatus.BAD,
                        'probability': 40.,
                    },
                    {
                        'id': None,
                        'pit_in_id': 4,
                        'competition_id': 3,
                        'step': 1,
                        'kart_status': KartStatus.UNKNOWN,
                        'probability': 10.,
                    },
                ],
            ),
        ])
    def test_add_many(
            self,
            competition_id: int,
            pit_in_id: int,
            models: List[AddStrategyPitsStats],
            expected_items: list,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method add_many."""
        manager = StrategyPitsKartsManager(db=db_context, logger=fake_logger)
        item_ids = manager.add_many(models, commit=True)

        for item_id, expected_item in zip(item_ids, expected_items):
            expected_item['id'] = item_id

        db_items = manager.get_strategy_by_pit_in(competition_id, pit_in_id)
        dict_items = [x.model_dump(exclude=self.EXCLUDE) for x in db_items]
        assert dict_items == expected_items


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

        dict_item = db_item.model_dump(exclude=self.EXCLUDE)
        assert dict_item == expected_item

    @pytest.mark.parametrize(
        'model, expected_item',
        [
            (
                AddStrategyPitsStats(  # model
                    pit_in_id=3,
                    best_time=59500,
                    avg_time=59800,
                ),
                {  # expected_item
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
        assert db_item is not None

        dict_item = db_item.model_dump(exclude=self.EXCLUDE)
        assert dict_item == expected_item

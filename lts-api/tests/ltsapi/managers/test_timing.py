import time
from typing import List, Optional
import pytest

from ltsapi.db import DBContext
from ltsapi.managers.timing import TimingManager
from ltsapi.models.enum import (
    CompetitionStage,
    KartStatus,
    LengthUnit,
)
from ltsapi.models.timing import UpdateLapTime
from tests.helpers import DatabaseTest
from tests.mocks.logging import FakeLogger


class TestTimingManager(DatabaseTest):
    """Test class ltsapi.managers.competitions.TimingManager."""

    EXCLUDE = {
        'insert_date': True,
        'update_date': True,
    }

    @pytest.mark.parametrize(
        'competition_id, expected_items',
        [
            (
                2,  # competition_id
                [
                    {
                        'team_id': 4,
                        'driver_id': 5,
                        'position': 1,
                        'time': 58800,
                        'best_time': 58800,
                        'lap': 2,
                        'interval': 0,
                        'interval_unit': LengthUnit.MILLIS.value,
                        'stage': CompetitionStage.RACE.value,
                        'pit_time': 0,
                        'kart_status': KartStatus.GOOD.value,
                        'fixed_kart_status': None,
                        'number_pits': 0,
                    },
                    {
                        'team_id': 5,
                        'driver_id': 7,
                        'position': 2,
                        'time': 59700,
                        'best_time': 59500,
                        'lap': 2,
                        'interval': 1400,
                        'interval_unit': LengthUnit.MILLIS.value,
                        'stage': CompetitionStage.RACE.value,
                        'pit_time': 0,
                        'kart_status': KartStatus.BAD.value,
                        'fixed_kart_status': None,
                        'number_pits': 0,
                    },
                ],
            ),
        ])
    def test_get_current_all_by_id(
            self,
            competition_id: int,
            expected_items: list,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method get_current_all_by_id."""
        manager = TimingManager(db=db_context, logger=fake_logger)
        dict_items = [x.dict(exclude=self.EXCLUDE)
                      for x in manager.get_current_all_by_id(competition_id)]
        assert dict_items == expected_items

    @pytest.mark.parametrize(
        'competition_id, team_id, driver_id, expected_item',
        [
            (
                2,  # competition_id
                5,  # team_id
                None,  # driver_id
                {
                    'team_id': 5,
                    'driver_id': 7,
                    'position': 2,
                    'time': 59700,
                    'best_time': 59500,
                    'lap': 2,
                    'interval': 1400,
                    'interval_unit': LengthUnit.MILLIS.value,
                    'stage': CompetitionStage.RACE.value,
                    'pit_time': 0,
                    'kart_status': KartStatus.BAD.value,
                    'fixed_kart_status': None,
                    'number_pits': 0,
                },
            ),
            (
                2,  # competition_id
                None,  # team_id
                7,  # driver_id
                {
                    'team_id': 5,
                    'driver_id': 7,
                    'position': 2,
                    'time': 59700,
                    'best_time': 59500,
                    'lap': 2,
                    'interval': 1400,
                    'interval_unit': LengthUnit.MILLIS.value,
                    'stage': CompetitionStage.RACE.value,
                    'pit_time': 0,
                    'kart_status': KartStatus.BAD.value,
                    'fixed_kart_status': None,
                    'number_pits': 0,
                },
            ),
        ])
    def test_get_current_single_by_id(
            self,
            competition_id: int,
            team_id: Optional[int],
            driver_id: Optional[int],
            expected_item: dict,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method get_current_single_by_id."""
        manager = TimingManager(db=db_context, logger=fake_logger)

        db_item = manager.get_current_single_by_id(
            competition_id, team_id=team_id, driver_id=driver_id)
        assert db_item is not None

        dict_item = db_item.dict(exclude=self.EXCLUDE)
        assert dict_item == expected_item

    @pytest.mark.parametrize(
        'competition_id, expected_items',
        [
            (
                2,  # competition_id
                [
                    {
                        'team_id': 4,
                        'driver_id': 5,
                        'position': 1,
                        'time': 0,
                        'best_time': 0,
                        'lap': 0,
                        'interval': 0,
                        'interval_unit': LengthUnit.MILLIS.value,
                        'stage': CompetitionStage.RACE.value,
                        'pit_time': 0,
                        'kart_status': KartStatus.UNKNOWN.value,
                        'fixed_kart_status': None,
                        'number_pits': 0,
                    },
                    {
                        'team_id': 5,
                        'driver_id': 7,
                        'position': 2,
                        'time': 0,
                        'best_time': 0,
                        'lap': 0,
                        'interval': 0,
                        'interval_unit': LengthUnit.MILLIS.value,
                        'stage': CompetitionStage.RACE.value,
                        'pit_time': 0,
                        'kart_status': KartStatus.UNKNOWN.value,
                        'fixed_kart_status': None,
                        'number_pits': 0,
                    },
                    {
                        'team_id': 4,
                        'driver_id': 5,
                        'position': 1,
                        'time': 59000,
                        'best_time': 59000,
                        'lap': 1,
                        'interval': 0,
                        'interval_unit': LengthUnit.MILLIS.value,
                        'stage': CompetitionStage.RACE.value,
                        'pit_time': 0,
                        'kart_status': KartStatus.UNKNOWN.value,
                        'fixed_kart_status': None,
                        'number_pits': 0,
                    },
                    {
                        'team_id': 5,
                        'driver_id': 7,
                        'position': 2,
                        'time': 59500,
                        'best_time': 59500,
                        'lap': 1,
                        'interval': 500,
                        'interval_unit': LengthUnit.MILLIS.value,
                        'stage': CompetitionStage.RACE.value,
                        'pit_time': 0,
                        'kart_status': KartStatus.UNKNOWN.value,
                        'fixed_kart_status': None,
                        'number_pits': 0,
                    },
                    {
                        'team_id': 4,
                        'driver_id': 5,
                        'position': 1,
                        'time': 58800,
                        'best_time': 58800,
                        'lap': 2,
                        'interval': 0,
                        'interval_unit': LengthUnit.MILLIS.value,
                        'stage': CompetitionStage.RACE.value,
                        'pit_time': 0,
                        'kart_status': KartStatus.GOOD.value,
                        'fixed_kart_status': None,
                        'number_pits': 0,
                    },
                    {
                        'team_id': 5,
                        'driver_id': 7,
                        'position': 2,
                        'time': 59700,
                        'best_time': 59500,
                        'lap': 2,
                        'interval': 1400,
                        'interval_unit': LengthUnit.MILLIS.value,
                        'stage': CompetitionStage.RACE.value,
                        'pit_time': 0,
                        'kart_status': KartStatus.BAD.value,
                        'fixed_kart_status': None,
                        'number_pits': 0,
                    },
                ],
            ),
        ])
    def test_get_history_by_id(
            self,
            competition_id: int,
            expected_items: List[dict],
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method get_history_by_id."""
        manager = TimingManager(db=db_context, logger=fake_logger)
        dict_items = [x.dict(exclude=self.EXCLUDE)
                      for x in manager.get_history_by_id(competition_id)]
        assert dict_items == expected_items

    @pytest.mark.parametrize(
        'competition_id, team_id, update_data, expected_item',
        [
            (
                2,  # competition_id
                4,  # team_id
                UpdateLapTime(
                    driver_id=5,
                    position=1,
                    time=58800,
                    best_time=58500,
                    lap=2,
                    interval=0,
                    interval_unit=LengthUnit.MILLIS,
                    stage=CompetitionStage.RACE,
                    pit_time=None,
                    kart_status=KartStatus.GOOD,
                    fixed_kart_status=None,
                    number_pits=0,
                ),
                {
                    'team_id': 4,
                    'driver_id': 5,
                    'position': 1,
                    'time': 58800,
                    'best_time': 58500,
                    'lap': 2,
                    'interval': 0,
                    'interval_unit': LengthUnit.MILLIS.value,
                    'stage': CompetitionStage.RACE.value,
                    'pit_time': None,
                    'kart_status': KartStatus.GOOD.value,
                    'fixed_kart_status': None,
                    'number_pits': 0,
                },
            ),
        ])
    def test_update_by_id(
            self,
            competition_id: int,
            team_id: int,
            update_data: UpdateLapTime,
            expected_item: dict,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method update_by_id."""
        manager = TimingManager(db=db_context, logger=fake_logger)

        before_item = manager.get_current_single_by_id(
            competition_id, team_id=team_id)
        assert before_item is not None

        time.sleep(1)
        manager.update_by_id(update_data, competition_id, team_id=team_id)

        after_item = manager.get_current_single_by_id(
            competition_id, team_id=team_id)
        assert after_item is not None
        dict_item = after_item.dict(exclude=self.EXCLUDE)

        assert dict_item == expected_item
        assert before_item.insert_date == after_item.insert_date
        assert before_item.update_date < after_item.update_date

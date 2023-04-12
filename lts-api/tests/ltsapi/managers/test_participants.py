import pytest
import time
from typing import List, Optional

from ltsapi.db import DBContext
from ltsapi.models.participants import (
    AddDriver,
    AddTeam,
    GetDriver,
    GetTeam,
    UpdateDriver,
    UpdateTeam,
)
from ltsapi.managers.participants import DriversManager, TeamsManager
from tests.helpers import DatabaseTestInit
from tests.mocks.logging import FakeLogger


class TestDriversManager(DatabaseTestInit):
    """Test class ltsapi.managers.competitions.DriversManager."""

    EXCLUDED_KEYS = {
        'insert_date': True,
        'update_date': True,
    }
    ALL_DRIVERS = [
        {
            'id': 1,
            'competition_id': 1,
            'team_id': 1,
            'participant_code': 'team-1',
            'name': 'CKM 1 Driver 1',
            'number': 41,
            'total_driving_time': 0,
            'partial_driving_time': 0,
            'reference_time_offset': 0,
        },
        {
            'id': 2,
            'competition_id': 1,
            'team_id': 1,
            'participant_code': 'team-1',
            'name': 'CKM 1 Driver 2',
            'number': 41,
            'total_driving_time': 0,
            'partial_driving_time': 0,
            'reference_time_offset': 0,
        },
        {
            'id': 3,
            'competition_id': 1,
            'team_id': 2,
            'participant_code': 'team-2',
            'name': 'CKM 2 Driver 1',
            'number': 42,
            'total_driving_time': 0,
            'partial_driving_time': 0,
            'reference_time_offset': 0,
        },
        {
            'id': 4,
            'competition_id': 1,
            'team_id': 2,
            'participant_code': 'team-2',
            'name': 'CKM 2 Driver 2',
            'number': 42,
            'total_driving_time': 0,
            'partial_driving_time': 0,
            'reference_time_offset': 0,
        },
        {
            'id': 5,
            'competition_id': 2,
            'team_id': 3,
            'participant_code': 'team-1',
            'name': 'CKM 1 Driver 1',
            'number': 41,
            'total_driving_time': 0,
            'partial_driving_time': 0,
            'reference_time_offset': 0,
        },
        {
            'id': 6,
            'competition_id': 2,
            'team_id': 3,
            'participant_code': 'team-1',
            'name': 'CKM 1 Driver 2',
            'number': 41,
            'total_driving_time': 0,
            'partial_driving_time': 0,
            'reference_time_offset': 0,
        },
        {
            'id': 7,
            'competition_id': 2,
            'team_id': 4,
            'participant_code': 'team-2',
            'name': 'CKM 2 Driver 1',
            'number': 42,
            'total_driving_time': 0,
            'partial_driving_time': 0,
            'reference_time_offset': 0,
        },
        {
            'id': 8,
            'competition_id': 2,
            'team_id': 4,
            'participant_code': 'team-2',
            'name': 'CKM 2 Driver 2',
            'number': 42,
            'total_driving_time': 0,
            'partial_driving_time': 0,
            'reference_time_offset': 0,
        },
        {
            'id': 9,
            'competition_id': 3,
            'team_id': 5,
            'participant_code': 'team-1',
            'name': 'CKM 1 Driver 1',
            'number': 41,
            'total_driving_time': 0,
            'partial_driving_time': 0,
            'reference_time_offset': 0,
        },
        {
            'id': 10,
            'competition_id': 3,
            'team_id': 5,
            'participant_code': 'team-1',
            'name': 'CKM 1 Driver 2',
            'number': 41,
            'total_driving_time': 0,
            'partial_driving_time': 0,
            'reference_time_offset': 0,
        },
    ]

    def test_get_all(
            self, db_context: DBContext, fake_logger: FakeLogger) -> None:
        """Test method get_all."""
        manager = DriversManager(db=db_context, logger=fake_logger)
        dict_items = [x.dict(exclude=self.EXCLUDED_KEYS)
                      for x in manager.get_all()]
        expected_items = self.ALL_DRIVERS
        assert dict_items == expected_items

    @pytest.mark.parametrize(
        'driver_id, team_id, competition_id, expected_item',
        [
            (
                2,  # driver_id
                1,  # team_id
                1,  # competition_id
                {
                    'id': 2,
                    'competition_id': 1,
                    'team_id': 1,
                    'participant_code': 'team-1',
                    'name': 'CKM 1 Driver 2',
                    'number': 41,
                    'total_driving_time': 0,
                    'partial_driving_time': 0,
                    'reference_time_offset': 0,
                },
            ),
        ])
    def test_get_by_id(
            self,
            driver_id: int,
            team_id: Optional[int],
            competition_id: Optional[int],
            expected_item: dict,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method get_by_id."""
        manager = DriversManager(db=db_context, logger=fake_logger)

        db_item = manager.get_by_id(
            driver_id, team_id=team_id, competition_id=competition_id)
        assert db_item is not None

        dict_item = db_item.dict(exclude=self.EXCLUDED_KEYS)
        assert dict_item == expected_item

    @pytest.mark.parametrize(
        'team_id, competition_id, expected_items',
        [
            (
                2,  # team_id
                1,  # competition_id
                [
                    {
                        'id': 3,
                        'competition_id': 1,
                        'team_id': 2,
                        'participant_code': 'team-2',
                        'name': 'CKM 2 Driver 1',
                        'number': 42,
                        'total_driving_time': 0,
                        'partial_driving_time': 0,
                        'reference_time_offset': 0,
                    },
                    {
                        'id': 4,
                        'competition_id': 1,
                        'team_id': 2,
                        'participant_code': 'team-2',
                        'name': 'CKM 2 Driver 2',
                        'number': 42,
                        'total_driving_time': 0,
                        'partial_driving_time': 0,
                        'reference_time_offset': 0,
                    },
                ],
            ),
        ])
    def test_get_by_team_id(
            self,
            team_id: int,
            competition_id: Optional[int],
            expected_items: List[GetDriver],
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method get_by_team_id."""
        manager = DriversManager(db=db_context, logger=fake_logger)
        dict_items = [x.dict(exclude=self.EXCLUDED_KEYS)
                      for x in manager.get_by_team_id(team_id, competition_id)]
        assert dict_items == expected_items

    @pytest.mark.parametrize(
        'competition_id, expected_items',
        [
            (
                3,  # competition_id
                [
                    {
                        'id': 9,
                        'competition_id': 3,
                        'team_id': 5,
                        'participant_code': 'team-1',
                        'name': 'CKM 1 Driver 1',
                        'number': 41,
                        'total_driving_time': 0,
                        'partial_driving_time': 0,
                        'reference_time_offset': 0,
                    },
                    {
                        'id': 10,
                        'competition_id': 3,
                        'team_id': 5,
                        'participant_code': 'team-1',
                        'name': 'CKM 1 Driver 2',
                        'number': 41,
                        'total_driving_time': 0,
                        'partial_driving_time': 0,
                        'reference_time_offset': 0,
                    },
                ],
            ),
        ])
    def test_get_by_competition_id(
            self,
            competition_id: int,
            expected_items: List[GetDriver],
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method get_by_competition_id."""
        manager = DriversManager(db=db_context, logger=fake_logger)
        dict_items = [x.dict(exclude=self.EXCLUDED_KEYS)
                      for x in manager.get_by_competition_id(competition_id)]
        assert dict_items == expected_items

    @pytest.mark.parametrize(
        'driver_name, team_id, competition_id, expected_item',
        [
            (
                'CKM 1 Driver 2',  # driver_name
                1,  # team_id
                1,  # competition_id
                {
                    'id': 2,
                    'competition_id': 1,
                    'team_id': 1,
                    'participant_code': 'team-1',
                    'name': 'CKM 1 Driver 2',
                    'number': 41,
                    'total_driving_time': 0,
                    'partial_driving_time': 0,
                    'reference_time_offset': 0,
                },
            ),
        ])
    def test_get_by_name(
            self,
            driver_name: str,
            team_id: Optional[int],
            competition_id: Optional[int],
            expected_item: dict,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method get_by_name."""
        manager = DriversManager(db=db_context, logger=fake_logger)

        db_item = manager.get_by_name(
            driver_name=driver_name,
            competition_id=competition_id,
            team_id=team_id)
        assert db_item is not None

        dict_item = db_item.dict(exclude=self.EXCLUDED_KEYS)
        assert dict_item == expected_item

    @pytest.mark.parametrize(
        'team_id, competition_id, model, expected_item',
        [
            (
                1,  # competition_id
                1,  # team_id
                AddDriver(
                    participant_code='team-1',
                    name='CKM 1 Driver 3',
                    number=41,
                    total_driving_time=0,
                    partial_driving_time=0,
                    reference_time_offset=0,
                ),
                {
                    'id': 2,
                    'competition_id': 1,
                    'team_id': 1,
                    'participant_code': 'team-1',
                    'name': 'CKM 1 Driver 3',
                    'number': 41,
                    'total_driving_time': 0,
                    'partial_driving_time': 0,
                    'reference_time_offset': 0,
                },
            ),
        ])
    def test_add_one(
            self,
            competition_id: int,
            team_id: Optional[int],
            model: AddDriver,
            expected_item: dict,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method add_one."""
        manager = DriversManager(db=db_context, logger=fake_logger)
        item_id = manager.add_one(model, competition_id, team_id, commit=True)

        expected_item['id'] = item_id
        db_item = manager.get_by_id(item_id, team_id, competition_id)
        assert db_item is not None

        dict_item = db_item.dict(exclude=self.EXCLUDED_KEYS)
        assert dict_item == expected_item

    @pytest.mark.parametrize(
        'competition_id, team_id, model, expected_error',
        [
            (
                2,  # competition_id
                4,  # team_id
                AddDriver(
                    participant_code='team-2',
                    name='CKM 2 Driver 1',
                    number=42,
                    total_driving_time=0,
                    partial_driving_time=0,
                    reference_time_offset=0,
                ),
                'The driver "CKM 2 Driver 1" (team=4) already exists.',
            ),
        ])
    def test_add_one_duplicated_code(
            self,
            competition_id: int,
            team_id: Optional[int],
            model: AddDriver,
            expected_error: str,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method add_one."""
        manager = DriversManager(db=db_context, logger=fake_logger)
        with pytest.raises(Exception) as e_info:
            manager.add_one(model, competition_id, team_id, commit=True)

        e: Exception = e_info.value
        assert str(e) == expected_error

    @pytest.mark.parametrize(
        'driver_id, team_id, competition_id, update_data, expected_item',
        [
            (
                2,  # driver_id
                1,  # team_id
                1,  # competition_id
                UpdateDriver(
                    participant_code=None,
                    name=None,
                    number=None,
                    total_driving_time=79000,
                    partial_driving_time=80000,
                    reference_time_offset=81000),
                {
                    'id': 2,
                    'team_id': 1,
                    'competition_id': 1,
                    'participant_code': 'team-1',
                    'name': 'CKM 1 Driver 2',
                    'number': 41,
                    'total_driving_time': 79000,
                    'partial_driving_time': 80000,
                    'reference_time_offset': 81000,
                },
            ),
            (
                2,  # driver_id
                1,  # team_id
                1,  # competition_id
                UpdateDriver(
                    participant_code='team-1-updated',
                    name='CKM 1 Driver 2 Updated',
                    number=51,
                    total_driving_time=79000,
                    partial_driving_time=80000,
                    reference_time_offset=81000),
                {
                    'id': 2,
                    'team_id': 1,
                    'competition_id': 1,
                    'participant_code': 'team-1-updated',
                    'name': 'CKM 1 Driver 2 Updated',
                    'number': 51,
                    'total_driving_time': 79000,
                    'partial_driving_time': 80000,
                    'reference_time_offset': 81000,
                },
            ),
        ])
    def test_update_by_id(
            self,
            driver_id: int,
            team_id: Optional[int],
            competition_id: Optional[int],
            update_data: UpdateDriver,
            expected_item: dict,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method update_by_id."""
        manager = DriversManager(db=db_context, logger=fake_logger)

        before_item = manager.get_by_id(driver_id, team_id, competition_id)
        assert before_item is not None

        time.sleep(1)
        manager.update_by_id(update_data, driver_id, team_id, competition_id)

        after_item = manager.get_by_id(driver_id, team_id, competition_id)
        assert after_item is not None
        dict_item = after_item.dict(exclude=self.EXCLUDED_KEYS)

        assert dict_item == expected_item
        assert before_item.insert_date == after_item.insert_date
        assert before_item.update_date < after_item.update_date


class TestTeamsManager(DatabaseTestInit):
    """Test class ltsapi.managers.competitions.TeamsManager."""

    EXCLUDED_KEYS = {
        'insert_date': True,
        'update_date': True,
    }
    ALL_TEAMS = [
        {
            'id': 1,
            'competition_id': 1,
            'participant_code': 'team-1',
            'name': 'CKM 1',
            'number': 41,
            'reference_time_offset': 0,
            'drivers': [],
        },
        {
            'id': 2,
            'competition_id': 1,
            'participant_code': 'team-2',
            'name': 'CKM 2',
            'number': 42,
            'reference_time_offset': 0,
            'drivers': [],
        },
        {
            'id': 3,
            'competition_id': 1,
            'participant_code': 'team-3',
            'name': 'CKM 3',
            'number': 43,
            'reference_time_offset': 0,
            'drivers': [],
        },
        {
            'id': 4,
            'competition_id': 2,
            'participant_code': 'team-1',
            'name': 'CKM 1',
            'number': 41,
            'reference_time_offset': 0,
            'drivers': [],
        },
        {
            'id': 5,
            'competition_id': 2,
            'participant_code': 'team-2',
            'name': 'CKM 2',
            'number': 42,
            'reference_time_offset': 0,
            'drivers': [],
        },
        {
            'id': 6,
            'competition_id': 3,
            'participant_code': 'team-1',
            'name': 'CKM 1',
            'number': 41,
            'reference_time_offset': 0,
            'drivers': [],
        },
    ]

    def test_get_all(
            self, db_context: DBContext, fake_logger: FakeLogger) -> None:
        """Test method get_all."""
        manager = TeamsManager(db=db_context, logger=fake_logger)
        dict_items = [x.dict(exclude=self.EXCLUDED_KEYS)
                      for x in manager.get_all()]
        expected_items = self.ALL_TEAMS
        assert dict_items == expected_items

    @pytest.mark.parametrize(
        'team_id, expected_item',
        [
            (
                2,  # team_id
                {
                    'id': 2,
                    'competition_id': 1,
                    'participant_code': 'team-2',
                    'name': 'CKM 2',
                    'number': 42,
                    'reference_time_offset': 0,
                    'drivers': [],
                },
            ),
        ])
    def test_get_by_id(
            self,
            team_id: int,
            expected_item: dict,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method get_by_id."""
        manager = TeamsManager(db=db_context, logger=fake_logger)

        db_item = manager.get_by_id(team_id)
        assert db_item is not None

        dict_item = db_item.dict(exclude=self.EXCLUDED_KEYS)
        assert dict_item == expected_item

    @pytest.mark.parametrize(
        'competition_id, expected_items',
        [
            (
                2,  # competition_id
                [
                    {
                        'id': 4,
                        'competition_id': 2,
                        'participant_code': 'team-1',
                        'name': 'CKM 1',
                        'number': 41,
                        'reference_time_offset': 0,
                        'drivers': [],
                    },
                    {
                        'id': 5,
                        'competition_id': 2,
                        'participant_code': 'team-2',
                        'name': 'CKM 2',
                        'number': 42,
                        'reference_time_offset': 0,
                        'drivers': [],
                    },
                ],
            ),
        ])
    def test_get_by_competition_id(
            self,
            competition_id: int,
            expected_items: List[GetTeam],
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method get_by_competition_id."""
        manager = TeamsManager(db=db_context, logger=fake_logger)
        dict_items = [x.dict(exclude=self.EXCLUDED_KEYS)
                      for x in manager.get_by_competition_id(competition_id)]
        assert dict_items == expected_items

    @pytest.mark.parametrize(
        'team_code, competition_id, expected_item',
        [
            (
                'team-2',  # team_code
                1,  # competition_id
                {
                    'id': 2,
                    'competition_id': 1,
                    'participant_code': 'team-2',
                    'name': 'CKM 2',
                    'number': 42,
                    'reference_time_offset': 0,
                    'drivers': [],
                },
            ),
        ])
    def test_get_by_code(
            self,
            team_code: str,
            competition_id: Optional[int],
            expected_item: GetTeam,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method get_by_code."""
        manager = TeamsManager(db=db_context, logger=fake_logger)
        db_item = manager.get_by_code(team_code, competition_id)
        assert db_item is not None

        dict_item = db_item.dict(exclude=self.EXCLUDED_KEYS)
        assert dict_item == expected_item

    @pytest.mark.parametrize(
        'competition_id, model, expected_item',
        [
            (
                3,  # competition_id
                AddTeam(
                    participant_code='team-2',
                    name='CKM 2',
                    number=42,
                    reference_time_offset=0,
                ),
                {
                    'id': None,
                    'competition_id': 3,
                    'participant_code': 'team-2',
                    'name': 'CKM 2',
                    'number': 42,
                    'reference_time_offset': 0,
                    'drivers': [],
                },
            ),
        ])
    def test_add_one(
            self,
            competition_id: Optional[int],
            model: AddTeam,
            expected_item: dict,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method add_one."""
        manager = TeamsManager(db=db_context, logger=fake_logger)
        item_id = manager.add_one(model, competition_id, commit=True)

        expected_item['id'] = item_id
        db_item = manager.get_by_id(item_id, competition_id)
        assert db_item is not None

        dict_item = db_item.dict(exclude=self.EXCLUDED_KEYS)
        assert dict_item == expected_item

    @pytest.mark.parametrize(
        'competition_id, model, expected_error',
        [
            (
                3,  # competition_id
                AddTeam(
                    participant_code='team-1',
                    name='CKM 1',
                    number=41,
                    reference_time_offset=0,
                ),
                'The team "team-1" (competition=3) already exists.',
            ),
        ])
    def test_add_one_duplicated_code(
            self,
            competition_id: int,
            model: AddTeam,
            expected_error: str,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method add_one."""
        manager = TeamsManager(db=db_context, logger=fake_logger)
        with pytest.raises(Exception) as e_info:
            manager.add_one(model, competition_id, commit=True)

        e: Exception = e_info.value
        assert str(e) == expected_error

    @pytest.mark.parametrize(
        'team_id, competition_id, update_data, expected_item',
        [
            (
                2,  # team_id
                1,  # competition_id
                UpdateTeam(
                    id=2,
                    name=None,
                    participant_code=None,
                    number=None,
                    reference_time_offset=78000,
                ),
                {
                    'id': 2,
                    'competition_id': 1,
                    'participant_code': 'team-2',
                    'name': 'CKM 2',
                    'number': 42,
                    'reference_time_offset': 78000,
                    'drivers': [],
                },
            ),
            (
                2,  # team_id
                1,  # competition_id
                UpdateTeam(
                    id=2,
                    name='CKM 2 Updated',
                    participant_code='team-2-updated',
                    number=52,
                    reference_time_offset=78000,
                ),
                {
                    'id': 2,
                    'competition_id': 1,
                    'participant_code': 'team-2-updated',
                    'name': 'CKM 2 Updated',
                    'number': 52,
                    'reference_time_offset': 78000,
                    'drivers': [],
                },
            ),
        ])
    def test_update_by_id(
            self,
            team_id: int,
            competition_id: int,
            update_data: UpdateTeam,
            expected_item: dict,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method update_by_id."""
        manager = TeamsManager(db=db_context, logger=fake_logger)

        before_item = manager.get_by_id(team_id, competition_id)
        assert before_item is not None

        time.sleep(1)
        manager.update_by_id(update_data, team_id, competition_id)

        after_item = manager.get_by_id(team_id, competition_id)
        assert after_item is not None
        dict_item = after_item.dict(exclude=self.EXCLUDED_KEYS)

        assert dict_item == expected_item
        assert before_item.insert_date == after_item.insert_date
        assert before_item.update_date < after_item.update_date
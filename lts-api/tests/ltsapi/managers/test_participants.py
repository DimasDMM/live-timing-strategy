import pytest
import time
from typing import Any

from ltsapi.db import DBContext
from ltsapi.models.filters import IdFilter
from ltsapi.models.participants import (
    AddDriver,
    AddTeam,
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
            'code': 'team-1',
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
            'code': 'team-1',
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
            'code': 'team-2',
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
            'code': 'team-2',
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
            'code': 'team-1',
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
            'code': 'team-1',
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
            'code': 'team-2',
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
            'code': 'team-2',
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
            'code': 'team-1',
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
            'code': 'team-1',
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

    def test_get_by_id(
            self, db_context: DBContext, fake_logger: FakeLogger) -> None:
        """Test method get_by_id."""
        manager = DriversManager(db=db_context, logger=fake_logger)
        filter = IdFilter(id=2)

        db_item = manager.get_by_id(filter)
        assert db_item is not None

        dict_item = db_item.dict(exclude=self.EXCLUDED_KEYS)
        expected_item = {
            'id': 2,
            'competition_id': 1,
            'team_id': 1,
            'code': 'team-1',
            'name': 'CKM 1 Driver 2',
            'number': 41,
            'total_driving_time': 0,
            'partial_driving_time': 0,
            'reference_time_offset': 0,
        }
        assert dict_item == expected_item

    def test_get_by_team_id(
            self, db_context: DBContext, fake_logger: FakeLogger) -> None:
        """Test method get_by_team_id."""
        team_id = 2

        manager = DriversManager(db=db_context, logger=fake_logger)
        filter = IdFilter(id=team_id)

        dict_items = [x.dict(exclude=self.EXCLUDED_KEYS)
                      for x in manager.get_by_team_id(filter)]
        expected_items = [x for x in self.ALL_DRIVERS
                          if x['team_id'] == team_id]
        assert dict_items == expected_items

    def test_get_by_competition_id(
            self, db_context: DBContext, fake_logger: FakeLogger) -> None:
        """Test method get_by_competition_id."""
        competition_id = 2

        manager = DriversManager(db=db_context, logger=fake_logger)
        filter = IdFilter(id=competition_id)

        dict_items = [x.dict(exclude=self.EXCLUDED_KEYS)
                      for x in manager.get_by_competition_id(filter)]
        expected_items = [x for x in self.ALL_DRIVERS
                          if x['competition_id'] == competition_id]
        assert dict_items == expected_items

    def test_add_one(
            self, db_context: DBContext, fake_logger: FakeLogger) -> None:
        """Test method add_one."""
        manager = DriversManager(db=db_context, logger=fake_logger)
        add_item = AddDriver(
            competition_id=1,
            team_id=1,
            code='team-1',
            name='CKM 1 Driver 3',
            number=41,
            total_driving_time=0,
            partial_driving_time=0,
            reference_time_offset=0,
        )

        manager.add_one(add_item, commit=True)

        filter = IdFilter(id=11)
        db_item = manager.get_by_id(filter)
        assert db_item is not None

        dict_item = db_item.dict(exclude=self.EXCLUDED_KEYS)
        expected_item = {
            'id': 11,
            'team_id': add_item.team_id,
            'competition_id': add_item.competition_id,
            'code': add_item.code,
            'name': add_item.name,
            'number': add_item.number,
            'total_driving_time': add_item.total_driving_time,
            'partial_driving_time': add_item.partial_driving_time,
            'reference_time_offset': add_item.reference_time_offset,
        }
        assert dict_item == expected_item

    def test_add_one_duplicated_code(
            self, db_context: DBContext, fake_logger: FakeLogger) -> None:
        """Test method add_one."""
        manager = DriversManager(db=db_context, logger=fake_logger)
        add_item = AddDriver(
            competition_id=1,
            team_id=2,
            code='team-2',
            name='CKM 2 Driver 1',
            number=42,
            total_driving_time=0,
            partial_driving_time=0,
            reference_time_offset=0,
        )

        with pytest.raises(Exception) as e_info:
            manager.add_one(add_item, commit=True)

        e: Exception = e_info.value
        assert (str(e) == f'The driver "{add_item.name}" '
                f'(team={add_item.team_id}) already exists.')

    @pytest.mark.parametrize(
        'update_data, expected_item',
        [
            (
                UpdateDriver(
                    id=2,
                    code=None,
                    name=None,
                    number=None,
                    total_driving_time=79000,
                    partial_driving_time=80000,
                    reference_time_offset=81000),
                {
                    'id': 2,
                    'team_id': 1,
                    'competition_id': 1,
                    'code': 'team-1',
                    'name': 'CKM 1 Driver 2',
                    'number': 41,
                    'total_driving_time': 79000,
                    'partial_driving_time': 80000,
                    'reference_time_offset': 81000,
                },
            ),
            (
                UpdateDriver(
                    id=2,
                    code='team-1-updated',
                    name='CKM 1 Driver 2 Updated',
                    number=51,
                    total_driving_time=79000,
                    partial_driving_time=80000,
                    reference_time_offset=81000),
                {
                    'id': 2,
                    'team_id': 1,
                    'competition_id': 1,
                    'code': 'team-1-updated',
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
            update_data: UpdateDriver,
            expected_item: dict,
            request: Any) -> None:
        """Test method update_by_id."""
        db_context = request.getfixturevalue('db_context')
        fake_logger = request.getfixturevalue('fake_logger')

        manager = DriversManager(db=db_context, logger=fake_logger)
        filter_id = IdFilter(id=update_data.id)

        before_item = manager.get_by_id(filter_id)
        assert before_item is not None

        time.sleep(1)
        manager.update_by_id(update_data)

        after_item = manager.get_by_id(filter_id)
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
            'code': 'team-1',
            'name': 'CKM 1',
            'number': 41,
            'reference_time_offset': 0,
            'drivers': [],
        },
        {
            'id': 2,
            'competition_id': 1,
            'code': 'team-2',
            'name': 'CKM 2',
            'number': 42,
            'reference_time_offset': 0,
            'drivers': [],
        },
        {
            'id': 3,
            'competition_id': 1,
            'code': 'team-3',
            'name': 'CKM 3',
            'number': 43,
            'reference_time_offset': 0,
            'drivers': [],
        },
        {
            'id': 4,
            'competition_id': 2,
            'code': 'team-1',
            'name': 'CKM 1',
            'number': 41,
            'reference_time_offset': 0,
            'drivers': [],
        },
        {
            'id': 5,
            'competition_id': 2,
            'code': 'team-2',
            'name': 'CKM 2',
            'number': 42,
            'reference_time_offset': 0,
            'drivers': [],
        },
        {
            'id': 6,
            'competition_id': 3,
            'code': 'team-1',
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

    def test_get_by_id(
            self, db_context: DBContext, fake_logger: FakeLogger) -> None:
        """Test method get_by_id."""
        manager = TeamsManager(db=db_context, logger=fake_logger)
        filter = IdFilter(id=2)

        db_item = manager.get_by_id(filter)
        assert db_item is not None

        dict_item = db_item.dict(exclude=self.EXCLUDED_KEYS)
        expected_item = {
            'id': 2,
            'competition_id': 1,
            'code': 'team-2',
            'name': 'CKM 2',
            'number': 42,
            'reference_time_offset': 0,
            'drivers': [],
        }
        assert dict_item == expected_item

    def test_get_by_competition_id(
            self, db_context: DBContext, fake_logger: FakeLogger) -> None:
        """Test method get_by_competition_id."""
        competition_id = 2

        manager = TeamsManager(db=db_context, logger=fake_logger)
        filter = IdFilter(id=competition_id)

        dict_items = [x.dict(exclude=self.EXCLUDED_KEYS)
                      for x in manager.get_by_competition_id(filter)]
        expected_items = [x for x in self.ALL_TEAMS
                          if x['competition_id'] == competition_id]
        assert dict_items == expected_items

    def test_add_one(
            self, db_context: DBContext, fake_logger: FakeLogger) -> None:
        """Test method add_one."""
        manager = TeamsManager(db=db_context, logger=fake_logger)
        add_item = AddTeam(
            competition_id=3,
            code='team-2',
            name='CKM 2',
            number=42,
            reference_time_offset=0,
        )

        manager.add_one(add_item, commit=True)

        filter = IdFilter(id=7)
        db_item = manager.get_by_id(filter)
        assert db_item is not None

        dict_item = db_item.dict(exclude=self.EXCLUDED_KEYS)
        expected_item = {
            'id': 7,
            'competition_id': add_item.competition_id,
            'code': add_item.code,
            'name': add_item.name,
            'number': add_item.number,
            'reference_time_offset': add_item.reference_time_offset,
            'drivers': [],
        }
        assert dict_item == expected_item

    def test_add_one_duplicated_code(
            self, db_context: DBContext, fake_logger: FakeLogger) -> None:
        """Test method add_one."""
        manager = TeamsManager(db=db_context, logger=fake_logger)
        add_item = AddTeam(
            competition_id=1,
            code='team-2',
            name='CKM 2',
            number=42,
            reference_time_offset=0,
        )

        with pytest.raises(Exception) as e_info:
            manager.add_one(add_item, commit=True)

        e: Exception = e_info.value
        assert (str(e) == f'The team "{add_item.code}" '
                f'(competition={add_item.competition_id}) already exists.')

    @pytest.mark.parametrize(
        'update_data, expected_item',
        [
            (
                UpdateTeam(
                    id=2,
                    name=None,
                    code=None,
                    number=None,
                    reference_time_offset=78000,
                ),
                {
                    'id': 2,
                    'competition_id': 1,
                    'code': 'team-2',
                    'name': 'CKM 2',
                    'number': 42,
                    'reference_time_offset': 78000,
                    'drivers': [],
                },
            ),
            (
                UpdateTeam(
                    id=2,
                    name='CKM 2 Updated',
                    code='team-2-updated',
                    number=52,
                    reference_time_offset=78000,
                ),
                {
                    'id': 2,
                    'competition_id': 1,
                    'code': 'team-2-updated',
                    'name': 'CKM 2 Updated',
                    'number': 52,
                    'reference_time_offset': 78000,
                    'drivers': [],
                },
            ),
        ])
    def test_update_by_id(
            self,
            update_data: UpdateTeam,
            expected_item: dict,
            request: Any) -> None:
        """Test method update_by_id."""
        db_context = request.getfixturevalue('db_context')
        fake_logger = request.getfixturevalue('fake_logger')

        manager = TeamsManager(db=db_context, logger=fake_logger)
        filter_id = IdFilter(id=update_data.id)

        before_item = manager.get_by_id(filter_id)
        assert before_item is not None

        time.sleep(1)
        manager.update_by_id(update_data)

        after_item = manager.get_by_id(filter_id)
        assert after_item is not None
        dict_item = after_item.dict(exclude=self.EXCLUDED_KEYS)

        assert dict_item == expected_item
        assert before_item.insert_date == after_item.insert_date
        assert before_item.update_date < after_item.update_date

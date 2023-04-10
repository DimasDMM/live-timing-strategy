import pytest
import time
from typing import Any, Optional

from ltsapi.db import DBContext
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

    def test_get_by_id(
            self, db_context: DBContext, fake_logger: FakeLogger) -> None:
        """Test method get_by_id."""
        driver_id = 2
        manager = DriversManager(db=db_context, logger=fake_logger)

        db_item = manager.get_by_id(driver_id)
        assert db_item is not None

        dict_item = db_item.dict(exclude=self.EXCLUDED_KEYS)
        expected_item = {
            'id': 2,
            'competition_id': 1,
            'team_id': 1,
            'participant_code': 'team-1',
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

        dict_items = [x.dict(exclude=self.EXCLUDED_KEYS)
                      for x in manager.get_by_team_id(team_id)]
        expected_items = [x for x in self.ALL_DRIVERS
                          if x['team_id'] == team_id]
        assert dict_items == expected_items

    def test_get_by_competition_id(
            self, db_context: DBContext, fake_logger: FakeLogger) -> None:
        """Test method get_by_competition_id."""
        competition_id = 2
        manager = DriversManager(db=db_context, logger=fake_logger)

        dict_items = [x.dict(exclude=self.EXCLUDED_KEYS)
                      for x in manager.get_by_competition_id(competition_id)]
        expected_items = [x for x in self.ALL_DRIVERS
                          if x['competition_id'] == competition_id]
        assert dict_items == expected_items

    def test_get_by_name(
            self, db_context: DBContext, fake_logger: FakeLogger) -> None:
        """Test method get_by_name."""
        driver_name = 'CKM 1 Driver 1'
        team_id = 1
        competition_id = 1
        manager = DriversManager(db=db_context, logger=fake_logger)

        db_item = manager.get_by_name(
            driver_name=driver_name,
            competition_id=competition_id,
            team_id=team_id)
        assert db_item is not None

        dict_item = db_item.dict(exclude=self.EXCLUDED_KEYS)
        expected_item = {
            'id': 1,
            'competition_id': 1,
            'team_id': 1,
            'participant_code': 'team-1',
            'name': 'CKM 1 Driver 1',
            'number': 41,
            'total_driving_time': 0,
            'partial_driving_time': 0,
            'reference_time_offset': 0,
        }
        assert dict_item == expected_item

    def test_add_one(
            self, db_context: DBContext, fake_logger: FakeLogger) -> None:
        """Test method add_one."""
        manager = DriversManager(db=db_context, logger=fake_logger)
        competition_id = 1
        team_id = 1
        add_item = AddDriver(
            participant_code='team-1',
            name='CKM 1 Driver 3',
            number=41,
            total_driving_time=0,
            partial_driving_time=0,
            reference_time_offset=0,
        )

        manager.add_one(add_item, competition_id, team_id, commit=True)

        driver_id = 11
        db_item = manager.get_by_id(driver_id, team_id, competition_id)
        assert db_item is not None

        dict_item = db_item.dict(exclude=self.EXCLUDED_KEYS)
        expected_item = {
            'id': 11,
            'team_id': team_id,
            'competition_id': competition_id,
            'participant_code': add_item.participant_code,
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
        competition_id = 1
        team_id = 2
        manager = DriversManager(db=db_context, logger=fake_logger)
        add_item = AddDriver(
            participant_code='team-2',
            name='CKM 2 Driver 1',
            number=42,
            total_driving_time=0,
            partial_driving_time=0,
            reference_time_offset=0,
        )

        with pytest.raises(Exception) as e_info:
            manager.add_one(add_item, competition_id, team_id, commit=True)

        e: Exception = e_info.value
        assert (str(e) == f'The driver "{add_item.name}" '
                f'(team={team_id}) already exists.')

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
            request: Any) -> None:
        """Test method update_by_id."""
        db_context = request.getfixturevalue('db_context')
        fake_logger = request.getfixturevalue('fake_logger')
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

    def test_get_by_id(
            self, db_context: DBContext, fake_logger: FakeLogger) -> None:
        """Test method get_by_id."""
        team_id = 2
        manager = TeamsManager(db=db_context, logger=fake_logger)

        db_item = manager.get_by_id(team_id)
        assert db_item is not None

        dict_item = db_item.dict(exclude=self.EXCLUDED_KEYS)
        expected_item = {
            'id': 2,
            'competition_id': 1,
            'participant_code': 'team-2',
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

        dict_items = [x.dict(exclude=self.EXCLUDED_KEYS)
                      for x in manager.get_by_competition_id(competition_id)]
        expected_items = [x for x in self.ALL_TEAMS
                          if x['competition_id'] == competition_id]
        assert dict_items == expected_items

    def test_get_by_code(
            self, db_context: DBContext, fake_logger: FakeLogger) -> None:
        """Test method get_by_code."""
        team_code = 'team-2'
        competition_id = 1
        manager = TeamsManager(db=db_context, logger=fake_logger)

        db_item = manager.get_by_code(team_code, competition_id)
        assert db_item is not None

        dict_item = db_item.dict(exclude=self.EXCLUDED_KEYS)
        expected_item = {
            'id': 2,
            'competition_id': 1,
            'participant_code': 'team-2',
            'name': 'CKM 2',
            'number': 42,
            'reference_time_offset': 0,
            'drivers': [],
        }
        assert dict_item == expected_item

    def test_add_one(
            self, db_context: DBContext, fake_logger: FakeLogger) -> None:
        """Test method add_one."""
        competition_id = 3
        team_id = 7
        manager = TeamsManager(db=db_context, logger=fake_logger)
        add_item = AddTeam(
            participant_code='team-2',
            name='CKM 2',
            number=42,
            reference_time_offset=0,
        )

        manager.add_one(add_item, competition_id, commit=True)

        db_item = manager.get_by_id(team_id, competition_id)
        assert db_item is not None

        dict_item = db_item.dict(exclude=self.EXCLUDED_KEYS)
        expected_item = {
            'id': team_id,
            'competition_id': competition_id,
            'participant_code': add_item.participant_code,
            'name': add_item.name,
            'number': add_item.number,
            'reference_time_offset': add_item.reference_time_offset,
            'drivers': [],
        }
        assert dict_item == expected_item

    def test_add_one_duplicated_code(
            self, db_context: DBContext, fake_logger: FakeLogger) -> None:
        """Test method add_one."""
        competition_id = 1
        manager = TeamsManager(db=db_context, logger=fake_logger)
        add_item = AddTeam(
            competition_id=competition_id,
            participant_code='team-2',
            name='CKM 2',
            number=42,
            reference_time_offset=0,
        )

        with pytest.raises(Exception) as e_info:
            manager.add_one(add_item, competition_id, commit=True)

        e: Exception = e_info.value
        assert (str(e) == f'The team "{add_item.participant_code}" '
                f'(competition={competition_id}) already exists.')

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
            request: Any) -> None:
        """Test method update_by_id."""
        db_context = request.getfixturevalue('db_context')
        fake_logger = request.getfixturevalue('fake_logger')
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

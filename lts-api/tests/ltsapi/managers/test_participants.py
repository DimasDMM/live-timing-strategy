import pytest

from ltsapi.db import DBContext
from ltsapi.models.filters import IdFilter
from ltsapi.models.participants import AddTeam
from ltsapi.managers.participants import TeamsManager
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
            'total_driving_time': 0,
            'partial_driving_time': 0,
            'reference_time_offset': 0,
        },
        {
            'id': 3,
            'competition_id': 1,
            'team_id': 2,
            'code': 'team-1',
            'name': 'CKM 1 Driver 1',
            'total_driving_time': 0,
            'partial_driving_time': 0,
            'reference_time_offset': 0,
        },
        {
            'id': 4,
            'competition_id': 1,
            'team_id': 2,
            'code': 'team-1',
            'name': 'CKM 1 Driver 2',
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
            'total_driving_time': 0,
            'partial_driving_time': 0,
            'reference_time_offset': 0,
        },
        {
            'id': 7,
            'competition_id': 2,
            'team_id': 4,
            'code': 'team-1',
            'name': 'CKM 1 Driver 1',
            'total_driving_time': 0,
            'partial_driving_time': 0,
            'reference_time_offset': 0,
        },
        {
            'id': 8,
            'competition_id': 2,
            'team_id': 4,
            'code': 'team-1',
            'name': 'CKM 1 Driver 2',
            'total_driving_time': 0,
            'partial_driving_time': 0,
            'reference_time_offset': 0,
        },
    ]


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
                f'(competition = {add_item.competition_id}) already exists.')

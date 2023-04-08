import pytest

from ltsapi.db import DBContext
from ltsapi.models.filters import CodeFilter, IdFilter
from ltsapi.models.competitions import AddCompetition
from ltsapi.managers.competitions import CompetitionManager
from tests.helpers import DatabaseTestInit
from tests.mocks.logging import FakeLogger


class TestCompetitionManager(DatabaseTestInit):
    """Test class ltsapi.managers.competitions.CompetitionManager."""

    EXCLUDED_KEYS = {
        'insert_date': True,
        'update_date': True,
        'track': {'insert_date', 'update_date'},
    }

    def test_get_all(
            self, db_context: DBContext, fake_logger: FakeLogger) -> None:
        """Test method get_all."""
        manager = CompetitionManager(db=db_context, logger=fake_logger)
        dict_items = [x.dict(exclude=self.EXCLUDED_KEYS)
                      for x in manager.get_all()]
        expected_items = [
            {
                'id': 1,
                'track': {'id': 1, 'name': 'Karting Los Santos'},
                'code': 'santos-endurance-2023-02-26',
                'name': 'Resistencia Los Santos 26-02-2023',
                'description': 'Resistencia de 3h en Karting Los Santos',
            },
            {
                'id': 2,
                'track': {'id': 1, 'name': 'Karting Los Santos'},
                'code': 'santos-endurance-2023-03-25',
                'name': 'Resistencia Los Santos 25-03-2023',
                'description': 'Resistencia de 3h en Karting Los Santos',
            },
            {
                'id': 3,
                'track': {'id': 2, 'name': 'Karting Burgueño'},
                'code': 'burgueno-endurance-2023-03-26',
                'name': 'Resistencia Burgueño 26-03-2023',
                'description': 'Resistencia de 3h en Karting Burgueño',
            },
        ]
        assert dict_items == expected_items

    def test_get_by_id(
            self, db_context: DBContext, fake_logger: FakeLogger) -> None:
        """Test method get_by_id."""
        manager = CompetitionManager(db=db_context, logger=fake_logger)
        filter = IdFilter(id=2)

        db_item = manager.get_by_id(filter)
        assert db_item is not None

        dict_item = db_item.dict(exclude=self.EXCLUDED_KEYS)
        expected_item = {
            'id': 2,
            'track': {'id': 1, 'name': 'Karting Los Santos'},
            'code': 'santos-endurance-2023-03-25',
            'name': 'Resistencia Los Santos 25-03-2023',
            'description': 'Resistencia de 3h en Karting Los Santos',
        }
        assert dict_item == expected_item

    def test_get_by_code(
            self, db_context: DBContext, fake_logger: FakeLogger) -> None:
        """Test method get_by_code."""
        manager = CompetitionManager(db=db_context, logger=fake_logger)
        filter = CodeFilter(code='burgueno-endurance-2023-03-26')

        db_item = manager.get_by_code(filter)
        assert db_item is not None

        dict_item = db_item.dict(exclude=self.EXCLUDED_KEYS)
        expected_item = {
            'id': 3,
            'track': {'id': 2, 'name': 'Karting Burgueño'},
            'code': 'burgueno-endurance-2023-03-26',
            'name': 'Resistencia Burgueño 26-03-2023',
            'description': 'Resistencia de 3h en Karting Burgueño',
        }
        assert dict_item == expected_item

    def test_add_one(
            self, db_context: DBContext, fake_logger: FakeLogger) -> None:
        """Test method add_one."""
        manager = CompetitionManager(db=db_context, logger=fake_logger)
        add_item = AddCompetition(
            track_id=2,
            code='add-one-competition',
            name='Added competition',
            description='This is a test of adding a competition',
        )

        manager.add_one(add_item, commit=True)

        filter = IdFilter(id=4)
        db_item = manager.get_by_id(filter)
        assert db_item is not None

        dict_item = db_item.dict(exclude=self.EXCLUDED_KEYS)
        expected_item = {
            'id': 4,
            'track': {'id': 2, 'name': 'Karting Burgueño'},
            'code': add_item.code,
            'name': add_item.name,
            'description': add_item.description,
        }
        assert dict_item == expected_item

    def test_add_one_duplicated_code(
            self, db_context: DBContext, fake_logger: FakeLogger) -> None:
        """Test method add_one."""
        competition_code = 'santos-endurance-2023-02-26'
        manager = CompetitionManager(db=db_context, logger=fake_logger)
        add_item = AddCompetition(
            track_id=2,
            code=competition_code,
            name='Duplicated competition',
            description='This is a test of adding a duplicated competition',
        )

        with pytest.raises(Exception) as e_info:
            manager.add_one(add_item, commit=True)

        e: Exception = e_info.value
        assert str(e) == f'The code "{competition_code}" already exists.'

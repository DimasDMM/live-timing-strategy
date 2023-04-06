from ltsapi.db import DBContext
from ltsapi.managers.competitions import CompetitionManager
from tests.helpers import DatabaseTestInit
from tests.mocks.logging import FakeLogger


class TestCompetitionManager(DatabaseTestInit):
    """Test class ltsapi.managers.competitions.CompetitionManager."""

    def test_get_all(
            self, db_context: DBContext, fake_logger: FakeLogger) -> None:
        """Test method get_all."""
        excluded = {
            'insert_date': True,
            'update_date': True,
            'track': {'insert_date', 'update_date'},
        }
        manager = CompetitionManager(db=db_context, logger=fake_logger)
        db_items = [x.dict(exclude=excluded)
                    for x in manager.get_all()]
        expected_items = [
            {
                'id': 1,
                'track': {'id': 1, 'name': 'Karting Los Santos'},
                'code': 'endurance-2023-02-26',
                'name': 'Resistencia Los Santos 26-02-2023',
                'description': 'Resistencia de 3h en Karting Los Santos',
            },
            {
                'id': 2,
                'track': {'id': 1, 'name': 'Karting Los Santos'},
                'code': 'endurance-2023-03-25',
                'name': 'Resistencia Los Santos 25-03-2023',
                'description': 'Resistencia de 3h en Karting Los Santos',
            },
            {
                'id': 3,
                'track': {'id': 2, 'name': 'Karting Burgueño'},
                'code': 'endurance-2023-03-26',
                'name': 'Resistencia Burgueño 26-03-2023',
                'description': 'Resistencia de 3h en Karting Burgueño',
            },
        ]
        assert db_items == expected_items

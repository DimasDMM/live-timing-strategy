import pytest
import time

from ltsapi.db import DBContext
from ltsapi.models.competitions import (
    AddCompetition,
    AddTrack,
    UpdateTrack,
)
from ltsapi.managers.competitions import (
    CompetitionsIndexManager,
    TracksManager,
)
from tests.helpers import DatabaseTestInit
from tests.mocks.logging import FakeLogger


class TestTracksManager(DatabaseTestInit):
    """Test class ltsapi.managers.competitions.TracksManager."""

    EXCLUDED_KEYS = {
        'insert_date': True,
        'update_date': True,
    }
    ALL_TRACKS = [
        {
            'id': 1,
            'name': 'Karting North',
        },
        {
            'id': 2,
            'name': 'Karting South',
        },
    ]

    def test_get_all(
            self, db_context: DBContext, fake_logger: FakeLogger) -> None:
        """Test method get_all."""
        manager = TracksManager(db=db_context, logger=fake_logger)
        dict_items = [x.dict(exclude=self.EXCLUDED_KEYS)
                      for x in manager.get_all()]
        assert dict_items == self.ALL_TRACKS

    @pytest.mark.parametrize(
        'track_id, expected_item',
        [
            (
                2,  # track_id
                {
                    'id': 2,
                    'name': 'Karting South',
                },
            ),
        ])
    def test_get_by_id(
            self,
            track_id: int,
            expected_item: dict,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method get_by_id."""
        manager = TracksManager(db=db_context, logger=fake_logger)

        db_item = manager.get_by_id(track_id)
        assert db_item is not None

        dict_item = db_item.dict(exclude=self.EXCLUDED_KEYS)
        assert dict_item == expected_item

    @pytest.mark.parametrize(
        'model, expected_item',
        [
            (
                AddTrack(
                    name='New track',
                ),
                {
                    'id': None,
                    'name': 'New track',
                },
            ),
        ])
    def test_add_one(
            self,
            model: AddTrack,
            expected_item: dict,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method add_one."""
        manager = TracksManager(db=db_context, logger=fake_logger)
        item_id = manager.add_one(model, commit=True)

        expected_item['id'] = item_id
        db_item = manager.get_by_id(item_id)
        assert db_item is not None

        dict_item = db_item.dict(exclude=self.EXCLUDED_KEYS)
        assert dict_item == expected_item

    @pytest.mark.parametrize(
        'track_id, update_data, expected_item, is_updated',
        [
            (
                2,  # track_id
                UpdateTrack(name=None),
                {
                    'id': 2,
                    'name': 'Karting South',
                },
                False,  # is_updated
            ),
            (
                2,  # track_id
                UpdateTrack(name='Karting South Updated'),
                {
                    'id': 2,
                    'name': 'Karting South Updated',
                },
                True,  # is_updated
            ),
        ])
    def test_update_by_id(
            self,
            track_id: int,
            update_data: UpdateTrack,
            expected_item: dict,
            is_updated: bool,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method update_by_id."""
        manager = TracksManager(db=db_context, logger=fake_logger)

        before_item = manager.get_by_id(track_id)
        assert before_item is not None

        time.sleep(1)
        manager.update_by_id(update_data, track_id)

        after_item = manager.get_by_id(track_id)
        assert after_item is not None
        dict_item = after_item.dict(exclude=self.EXCLUDED_KEYS)

        assert dict_item == expected_item
        assert before_item.insert_date == after_item.insert_date
        if is_updated:
            assert before_item.update_date < after_item.update_date
        else:
            assert before_item.update_date == after_item.update_date


class TestCompetitionManager(DatabaseTestInit):
    """Test class ltsapi.managers.competitions.CompetitionManager."""

    ALL_COMPETITIONS = [
        {
            'id': 1,
            'track': {'id': 1, 'name': 'Karting North'},
            'competition_code': 'north-endurance-2023-02-26',
            'name': 'Endurance North 26-02-2023',
            'description': 'Endurance in Karting North',
        },
        {
            'id': 2,
            'track': {'id': 1, 'name': 'Karting North'},
            'competition_code': 'north-endurance-2023-03-25',
            'name': 'Endurance North 25-03-2023',
            'description': 'Endurance in Karting North',
        },
        {
            'id': 3,
            'track': {'id': 2, 'name': 'Karting South'},
            'competition_code': 'south-endurance-2023-03-26',
            'name': 'Endurance South 26-03-2023',
            'description': 'Endurance in Karting South',
        },
    ]
    EXCLUDED_KEYS = {
        'insert_date': True,
        'update_date': True,
        'track': {'insert_date', 'update_date'},
    }

    def test_get_all(
            self, db_context: DBContext, fake_logger: FakeLogger) -> None:
        """Test method get_all."""
        manager = CompetitionsIndexManager(db=db_context, logger=fake_logger)
        dict_items = [x.dict(exclude=self.EXCLUDED_KEYS)
                      for x in manager.get_all()]
        assert dict_items == self.ALL_COMPETITIONS

    @pytest.mark.parametrize(
        'competition_id, expected_item',
        [
            (
                2,  # competition_id
                {
                    'id': 2,
                    'track': {'id': 1, 'name': 'Karting North'},
                    'competition_code': 'north-endurance-2023-03-25',
                    'name': 'Endurance North 25-03-2023',
                    'description': 'Endurance in Karting North',
                },
            ),
        ])
    def test_get_by_id(
            self,
            competition_id: int,
            expected_item: dict,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method get_by_id."""
        manager = CompetitionsIndexManager(db=db_context, logger=fake_logger)

        db_item = manager.get_by_id(competition_id)
        assert db_item is not None

        dict_item = db_item.dict(exclude=self.EXCLUDED_KEYS)
        assert dict_item == expected_item

    @pytest.mark.parametrize(
        'competition_code, expected_item',
        [
            (
                'north-endurance-2023-03-25',  # competition_code
                {
                    'id': 2,
                    'track': {'id': 1, 'name': 'Karting North'},
                    'competition_code': 'north-endurance-2023-03-25',
                    'name': 'Endurance North 25-03-2023',
                    'description': 'Endurance in Karting North',
                },
            ),
        ])
    def test_get_by_code(
            self,
            competition_code: str,
            expected_item: dict,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method get_by_code."""
        manager = CompetitionsIndexManager(db=db_context, logger=fake_logger)

        db_item = manager.get_by_code(competition_code)
        assert db_item is not None

        dict_item = db_item.dict(exclude=self.EXCLUDED_KEYS)
        assert dict_item == expected_item

    @pytest.mark.parametrize(
        'model, expected_item',
        [
            (
                AddCompetition(
                    track_id=2,
                    competition_code='add-one-competition',
                    name='Added competition',
                    description='This is a test',
                ),
                {
                    'id': None,
                    'track': {'id': 2, 'name': 'Karting South'},
                    'competition_code': 'add-one-competition',
                    'name': 'Added competition',
                    'description': 'This is a test',
                },
            ),
        ])
    def test_add_one(
            self,
            model: AddCompetition,
            expected_item: dict,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method add_one."""
        manager = CompetitionsIndexManager(db=db_context, logger=fake_logger)
        item_id = manager.add_one(model, commit=True)

        expected_item['id'] = item_id
        db_item = manager.get_by_id(item_id)
        assert db_item is not None

        dict_item = db_item.dict(exclude=self.EXCLUDED_KEYS)
        assert dict_item == expected_item

    @pytest.mark.parametrize(
        'model, expected_error',
        [
            (
                AddCompetition(
                    track_id=2,
                    competition_code='north-endurance-2023-02-26',
                    name='Duplicated competition',
                    description='This is a test',
                ),
                ('There is already a competition with the '
                 'code "north-endurance-2023-02-26".'),
            ),
        ])
    def test_add_one_duplicated_code(
            self,
            model: AddCompetition,
            expected_error: str,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method add_one."""
        manager = CompetitionsIndexManager(db=db_context, logger=fake_logger)
        with pytest.raises(Exception) as e_info:
            manager.add_one(model, commit=True)

        e: Exception = e_info.value
        assert str(e) == expected_error

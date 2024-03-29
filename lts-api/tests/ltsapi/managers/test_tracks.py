import pytest
import time

from ltsapi.db import DBContext
from ltsapi.models.tracks import (
    AddTrack,
    UpdateTrack,
)
from ltsapi.managers.tracks import TracksManager
from tests.helpers import DatabaseTest
from tests.mocks.logging import FakeLogger


class TestTracksManager(DatabaseTest):
    """Test class ltsapi.managers.tracks.TracksManager."""

    EXCLUDE = {
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
        dict_items = [x.model_dump(exclude=self.EXCLUDE)
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

        dict_item = db_item.model_dump(exclude=self.EXCLUDE)
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

        dict_item = db_item.model_dump(exclude=self.EXCLUDE)
        assert dict_item == expected_item

    @pytest.mark.parametrize(
        'track_id, update_data, expected_item',
        [
            (
                2,  # track_id
                UpdateTrack(name='Karting South Updated'),
                {
                    'id': 2,
                    'name': 'Karting South Updated',
                },
            ),
        ])
    def test_update_by_id(
            self,
            track_id: int,
            update_data: UpdateTrack,
            expected_item: dict,
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
        dict_item = after_item.model_dump(exclude=self.EXCLUDE)

        assert dict_item == expected_item
        assert before_item.insert_date == after_item.insert_date
        assert before_item.update_date < after_item.update_date

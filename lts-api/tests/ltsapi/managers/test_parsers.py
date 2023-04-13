import pytest
import time

from ltsapi.db import DBContext
from ltsapi.models.parsers import (
    AddParserSetting,
    UpdateParserSetting,
)
from ltsapi.managers.parsers import ParsersSettingsManager
from tests.helpers import DatabaseTestInit
from tests.mocks.logging import FakeLogger


class TestParsersSettingsManager(DatabaseTestInit):
    """Test class ltsapi.managers.parsers.ParsersSettingsManager."""

    EXCLUDED_KEYS = {
        'insert_date': True,
        'update_date': True,
    }

    @pytest.mark.parametrize(
        'setting_name, competition_id, expected_item',
        [
            (
                'sample-setting-1',  # setting_name
                2,  # competition_id
                {
                    'name': 'sample-setting-1',
                    'value': 'sample-value-1',
                },
            ),
        ])
    def test_get_by_name(
            self,
            setting_name: str,
            competition_id: int,
            expected_item: dict,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method get_by_name."""
        manager = ParsersSettingsManager(db=db_context, logger=fake_logger)

        db_item = manager.get_by_name(setting_name, competition_id)
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
                        'name': 'sample-setting-1',
                        'value': 'sample-value-1',
                    },
                    {
                        'name': 'sample-setting-2',
                        'value': 'sample-value-2',
                    },
                ],
            ),
        ])
    def test_get_by_competition(
            self,
            competition_id: int,
            expected_items: list,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method get_by_competition."""
        manager = ParsersSettingsManager(db=db_context, logger=fake_logger)
        dict_items = [x.dict(exclude=self.EXCLUDED_KEYS)
                      for x in manager.get_by_competition(competition_id)]
        assert dict_items == expected_items

    @pytest.mark.parametrize(
        'competition_id, model, expected_item',
        [
            (
                2,  # competition_id
                AddParserSetting(
                    name='new-name',
                    value='new-value',
                ),
                {
                    'name': 'new-name',
                    'value': 'new-value',
                },
            ),
        ])
    def test_add_one(
            self,
            competition_id: int,
            model: AddParserSetting,
            expected_item: dict,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method add_one."""
        manager = ParsersSettingsManager(db=db_context, logger=fake_logger)
        _ = manager.add_one(model, competition_id, commit=True)

        db_item = manager.get_by_name(model.name, competition_id)
        assert db_item is not None

        dict_item = db_item.dict(exclude=self.EXCLUDED_KEYS)
        assert dict_item == expected_item

    @pytest.mark.parametrize(
        'competition_id, setting_name, update_data, expected_item, is_updated',
        [
            (
                2,  # competition_id
                'sample-setting-1',  # setting_name
                UpdateParserSetting(
                    value=None,
                ),
                {
                    'name': 'sample-setting-1',
                    'value': 'sample-value-1',
                },
                False,  # is_updated
            ),
            (
                2,  # competition_id
                'sample-setting-1',  # setting_name
                UpdateParserSetting(
                    value='sample-value-1-updated',
                ),
                {
                    'name': 'sample-setting-1',
                    'value': 'sample-value-1-updated',
                },
                True,  # is_updated
            ),
        ])
    def test_update_by_name(
            self,
            competition_id: int,
            setting_name: str,
            update_data: UpdateParserSetting,
            expected_item: dict,
            is_updated: bool,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method update_by_name."""
        manager = ParsersSettingsManager(db=db_context, logger=fake_logger)

        before_item = manager.get_by_name(
            setting_name=setting_name, competition_id=competition_id)
        assert before_item is not None

        time.sleep(1)
        manager.update_by_name(
            update_data,
            setting_name=setting_name,
            competition_id=competition_id)

        after_item = manager.get_by_name(
            setting_name=setting_name, competition_id=competition_id)
        assert after_item is not None
        dict_item = after_item.dict(exclude=self.EXCLUDED_KEYS)

        assert dict_item == expected_item
        assert before_item.insert_date == after_item.insert_date
        if is_updated:
            assert before_item.update_date < after_item.update_date
        else:
            assert before_item.update_date == after_item.update_date

    @pytest.mark.parametrize(
        'competition_id',
        [
            2,  # competition_id
        ])
    def test_delete_by_competition(
            self,
            competition_id: int,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method delete_by_competition."""
        manager = ParsersSettingsManager(db=db_context, logger=fake_logger)

        # Check that there are settings before deleting
        items = manager.get_by_competition(competition_id=competition_id)
        assert len(items) > 0

        # Do deletion
        manager.delete_by_competition(competition_id=competition_id)

        # Check that the data was removed correctly
        items = manager.get_by_competition(competition_id=competition_id)
        assert len(items) == 0

import pytest

from ltsapi.db import DBContext
from ltsapi.managers.auth import AuthManager
from ltsapi.models.enum import AuthRole
from tests.fixtures import AUTH_BEARER, AUTH_KEY_BATCH, AUTH_KEY_VIEWER
from tests.helpers import DatabaseTest
from tests.mocks.logging import FakeLogger


class TestAuthManager(DatabaseTest):
    """Test class ltsapi.managers.tracks.AuthManager."""

    @pytest.mark.parametrize(
        'key, expected_item',
        [
            (
                AUTH_KEY_BATCH,  # key
                {
                    'bearer': None,
                    'name': 'Test batch without bearer',
                    'role': 'batch',
                },
            ),
        ])
    def test_get_by_key(
            self,
            key: int,
            expected_item: dict,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method get_by_key."""
        manager = AuthManager(db=db_context, logger=fake_logger)

        db_item = manager.get_by_key(key)
        assert db_item is not None

        dict_item = db_item.dict()
        assert dict_item == expected_item

    def test_refresh_bearer_when_batch_role(
            self,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method refresh_bearer when the role is batch."""
        key_role_batch = AUTH_KEY_BATCH
        manager = AuthManager(db=db_context, logger=fake_logger)

        first_model = manager.refresh_bearer(key_role_batch)
        assert first_model is not None
        assert first_model.role == AuthRole.BATCH

        second_model = manager.refresh_bearer(key_role_batch)
        assert second_model is not None

        assert first_model.bearer == second_model.bearer
        assert first_model.name == second_model.name
        assert first_model.role == second_model.role

    def test_refresh_bearer_when_viewer_role(
            self,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method refresh_bearer when the role is viewer."""
        key_role_viewer = AUTH_KEY_VIEWER
        manager = AuthManager(db=db_context, logger=fake_logger)

        first_model = manager.refresh_bearer(key_role_viewer)
        assert first_model is not None
        assert first_model.role == AuthRole.VIEWER

        second_model = manager.refresh_bearer(key_role_viewer)
        assert second_model is not None

        assert first_model.bearer != second_model.bearer
        assert first_model.name == second_model.name
        assert first_model.role == second_model.role

    @pytest.mark.parametrize(
        'bearer, expected_item',
        [
            (
                f'Bearer {AUTH_BEARER}',
                {
                    'name': 'Test batch with bearer',
                    'role': 'batch',
                },
            ),
        ])
    def test_get_by_bearer(
            self,
            bearer: int,
            expected_item: dict,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method get_by_bearer."""
        manager = AuthManager(db=db_context, logger=fake_logger)

        db_item = manager.get_by_bearer(bearer)
        assert db_item is not None

        dict_item = db_item.dict()
        assert dict_item == expected_item

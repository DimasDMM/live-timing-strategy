import pytest

from ltsapi.db import DBContext
from ltsapi.managers.auth import AuthManager
from tests.fixtures import AUTH_BEARER
from tests.helpers import DatabaseTest
from tests.mocks.logging import FakeLogger


class TestAuthManager(DatabaseTest):
    """Test class ltsapi.managers.tracks.AuthManager."""

    @pytest.mark.parametrize(
        'key, expected_item',
        [
            (
                'd265aed699f7409ac0ec6fe07ee9cb11',  # key
                {
                    'bearer': None,
                    'name': 'Test',
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

    @pytest.mark.parametrize(
        'key',
        [
            'd265aed699f7409ac0ec6fe07ee9cb11',  # key
        ])
    def test_refresh_bearer(
            self,
            key: int,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method refresh_bearer."""
        manager = AuthManager(db=db_context, logger=fake_logger)

        old_item = manager.get_by_key(key)
        assert old_item is not None

        new_item = manager.refresh_bearer(key)
        assert new_item is not None
        assert old_item.bearer != new_item.bearer

    @pytest.mark.parametrize(
        'bearer, expected_item',
        [
            (
                f'Bearer {AUTH_BEARER}',
                {
                    'bearer': f'{AUTH_BEARER}',
                    'name': 'Test authenticated',
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

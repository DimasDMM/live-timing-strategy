import os
import pytest

from ltsapi.db import DBContext
from tests.helpers import DatabaseTestInit
from tests.mocks.logging import FakeLogger


@pytest.fixture
def fake_logger() -> FakeLogger:
    """Build a fake logger."""
    return FakeLogger()


@pytest.fixture(scope='class')
def db_context() -> DBContext:
    """Build a context to manage database connections."""
    return DBContext(
        host=os.environ.get('DB_HOST', None),
        port=os.environ.get('DB_PORT', None),
        user=os.environ.get('DB_USER', None),
        password=os.environ.get('DB_PASS', None),
        database=DatabaseTestInit.DATABASE_NAME,
        logger=FakeLogger(),
    )

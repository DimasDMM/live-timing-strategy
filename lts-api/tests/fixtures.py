import os
import pytest

from ltsapi.db import DBContext
from tests.helpers import DatabaseTest
from tests.mocks.logging import FakeLogger


@pytest.fixture
def fake_logger() -> FakeLogger:
    """Build a fake logger."""
    return FakeLogger()


@pytest.fixture(scope='function')
def db_context() -> DBContext:
    """Build a context to manage database connections."""
    db = DBContext(
        host=os.environ.get('DB_HOST', None),
        port=os.environ.get('DB_PORT', None),
        user=os.environ.get('DB_USER', None),
        password=os.environ.get('DB_PASS', None),
        database=DatabaseTest.DATABASE_NAME,
        logger=FakeLogger(),
    )
    with db:
        yield db

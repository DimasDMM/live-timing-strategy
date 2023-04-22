import os
import pytest

from ltsapi.db import DBContext
from tests.helpers import DatabaseTest
from tests.mocks.logging import FakeLogger

# Sample code of a competition for testing
TEST_COMPETITION_CODE = 'sample-code'

# Bearer token and API key included in the sample data for testing
AUTH_BEARER = 'e1ec4ca719196937f17f9914bf5a2a8c072ba0f9bc9225875e6a1286b2f350e9'
AUTH_KEY = 'd265aed699f7409ac0ec6fe07ee9cb11'


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

import pytest

from ltspipe.data.auth import AuthData, AuthRole
from ltspipe.messages import Message, MessageSource

# Sample code of a competition for testing
TEST_COMPETITION_CODE = 'sample-code'

# Bearer token in the sample data for testing
AUTH_BEARER = 'e1ec4ca719196937f17f9914bf5a2a8c072ba0f9bc9225875e6a1286b2f350e9'

# API key included in the sample data
AUTH_KEY = '912ec803b2ce49e4a541068d495ab570'


@pytest.fixture
def sample_auth_data() -> AuthData:
    """Build a sample auth data."""
    return AuthData(
        bearer=AUTH_BEARER,
        name='Test',
        role=AuthRole.BATCH,
    )


@pytest.fixture
def sample_message() -> Message:
    """Build a sample message."""
    return Message(
        competition_code=TEST_COMPETITION_CODE,
        data='sample-data',
        source=MessageSource.SOURCE_DUMMY,
        created_at=1679944690.8801994,
        updated_at=1679944719.1858709,
        error_description=None,
        error_traceback=None,
    )

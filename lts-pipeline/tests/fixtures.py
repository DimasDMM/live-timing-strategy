import os
import pytest

from ltspipe.messages import Message, MessageSource

# Sample code of a competition for testing
TEST_COMPETITION_CODE = 'competition-code'

# API key included in the sample data
AUTH_KEY = '6a204bd89f3c8348afd5c77c717a097a'

# API, Websocket and Kafka when they are real or mocked
API_LTS = os.environ.get('API_LTS', '')
MOCK_KAFKA = ['localhost:29092']
MOCK_WS = 'ws://localhost:28000/ws/'

assert API_LTS != '', 'Environment variable "API_LTS" must be set'


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

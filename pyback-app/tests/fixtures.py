import pytest

from pyback.messages import Message, MessageSource


@pytest.fixture
def sample_message() -> Message:
    """Build a sample message."""
    return Message(
        competition_code='sample-code',
        data='sample-data',
        source=MessageSource.SOURCE_DUMMY,
        created_at=1679944690.8801994,
        updated_at=1679944719.1858709,
        error_description=None,
        error_traceback=None,
    )

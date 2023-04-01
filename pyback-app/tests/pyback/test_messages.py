import json
from datetime import datetime
import pytest

from pyback.messages import Message
from pyback.messages import MessageSource


class TestMessage:
    """Test pyback.messages.Message class."""

    def test_init(self) -> None:
        """Test constructor."""
        event_code = 'sample-code'
        data = 'Hello, World!'
        source = MessageSource.SOURCE_DUMMY
        created_at = datetime.utcnow().timestamp()
        updated_at = datetime.utcnow().timestamp()
        error_description = 'This is a sample error description'
        error_traceback = 'Sample error trace'
        message = Message(
            event_code,
            data,
            source,
            created_at,
            updated_at,
            error_description,
            error_traceback)

        assert message.get_event_code() == event_code
        assert message.get_data() == data
        assert message.get_source() == source
        assert message.get_created_at() == created_at
        assert message.get_updated_at() == updated_at
        assert message.get_error_description() == error_description
        assert message.get_error_traceback() == error_traceback

    def test_encode(self) -> None:
        """Test encoding message."""
        event_code = 'sample-code'
        data = 'Hello, World!'
        source = MessageSource.SOURCE_DUMMY
        created_at = datetime.utcnow().timestamp()
        updated_at = datetime.utcnow().timestamp()
        error_description = 'This is a sample error description'
        error_traceback = 'Sample error trace'
        message = Message(
            event_code,
            data,
            source,
            created_at,
            updated_at,
            error_description,
            error_traceback)
        expected_result = json.dumps({
            'event_code': event_code,
            'data': data,
            'source': source.value,
            'created_at': created_at,
            'updated_at': updated_at,
            'error_description': error_description,
            'error_traceback': error_traceback,
        })

        assert message.encode() == expected_result

    def test_decode(self) -> None:
        """Test decoding message."""
        event_code = 'sample-code'
        data = 'Hello, World!'
        source = MessageSource.SOURCE_DUMMY
        created_at = datetime.utcnow().timestamp()
        updated_at = datetime.utcnow().timestamp()
        error_description = 'This is a sample error description'
        error_traceback = 'Sample error trace'
        message = Message(
            event_code,
            data,
            source,
            created_at,
            updated_at,
            error_description,
            error_traceback)
        encoded_message = message.encode()
        decoded_message: Message = Message.decode(encoded_message)

        assert decoded_message.get_event_code() == event_code
        assert decoded_message.get_data() == data
        assert decoded_message.get_source() == source
        assert decoded_message.get_created_at() == created_at
        assert decoded_message.get_updated_at() == updated_at
        assert decoded_message.get_error_description() == error_description
        assert decoded_message.get_error_traceback() == error_traceback

    def test_decode_with_missing_key(self) -> None:
        """Test decoding a message with a missing key."""
        encoded_message = json.dumps({
            'event_code': 'sample-code',
            'data': 'Hello, World!',
            'source': MessageSource.SOURCE_DUMMY.value,
            'created_at': datetime.utcnow().timestamp(),
        })
        with pytest.raises(Exception) as e_info:
            _ = Message.decode(encoded_message)
        exception: Exception = e_info.value
        assert str(exception).startswith('Key "updated_at" does not exist in:')

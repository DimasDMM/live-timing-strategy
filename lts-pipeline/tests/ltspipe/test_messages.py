from datetime import datetime
import json
import pytest

from ltspipe.data.actions import Action, ActionType
from ltspipe.data.competitions import (
    CompetitionStage,
    CompetitionStatus,
    DiffLap,
    InitialData,
    Participant,
)
from ltspipe.data.enum import LengthUnit
from ltspipe.messages import Message, MessageDecoder, MessageSource


class TestMessage:
    """Test ltspipe.messages.Message class."""

    def test_init(self) -> None:
        """Test constructor."""
        competition_code = 'sample-code'
        data = 'Hello, World!'
        source = MessageSource.SOURCE_DUMMY
        created_at = datetime.utcnow().timestamp()
        updated_at = datetime.utcnow().timestamp()
        error_description = 'This is a sample error description'
        error_traceback = 'Sample error trace'
        message = Message(
            competition_code=competition_code,
            data=data,
            source=source,
            created_at=created_at,
            updated_at=updated_at,
            error_description=error_description,
            error_traceback=error_traceback)

        assert message.competition_code == competition_code
        assert message.data == data
        assert message.source == source
        assert message.created_at == created_at
        assert message.updated_at == updated_at
        assert message.error_description == error_description
        assert message.error_traceback == error_traceback

    def test_encode(self) -> None:
        """Test encoding message."""
        competition_code = 'sample-code'
        data = 'Hello, World!'
        source = MessageSource.SOURCE_DUMMY
        created_at = datetime.utcnow().timestamp()
        updated_at = datetime.utcnow().timestamp()
        decoder = None
        error_description = 'This is a sample error description'
        error_traceback = 'Sample error trace'

        message = Message(
            competition_code=competition_code,
            data=data,
            source=source,
            created_at=created_at,
            updated_at=updated_at,
            decoder=decoder,
            error_description=error_description,
            error_traceback=error_traceback)

        expected_result = json.dumps({
            'competition_code': competition_code,
            'data': data,
            'source': source.value,
            'created_at': created_at,
            'updated_at': updated_at,
            'decoder': decoder,
            'error_description': error_description,
            'error_traceback': error_traceback,
        })

        assert message.encode() == expected_result

    @pytest.mark.parametrize(
        ('message'),
        [
            Message(
                competition_code='sample-code',
                data='Hello, world',
                source=MessageSource.SOURCE_DUMMY,
                created_at=1679944690.8801994,
                updated_at=1679944690.8801994,
                decoder=None,
                error_description='This is a sample description',
                error_traceback='Sample error trace'),
            Message(
                competition_code='sample-code',
                data=Action(
                    type=ActionType.INITIALIZE,
                    data=InitialData(
                        competition_code='sample-code',
                        reference_time=None,
                        reference_current_offset=None,
                        stage=CompetitionStage.QUALIFYING,
                        status=CompetitionStatus.ONGOING,
                        remaining_length=DiffLap(
                            value=10,
                            unit=LengthUnit.LAPS,
                        ),
                        participants={
                            'r5625': Participant(
                                best_time=64882,  # 1:04.882
                                gap=DiffLap(value=0, unit=LengthUnit.MILLIS),
                                interval=DiffLap(
                                    value=0, unit=LengthUnit.MILLIS),
                                kart_number=1,
                                laps=5,
                                last_lap_time=65142,  # 1:05.142
                                number_pits=2,
                                participant_code='r5625',
                                ranking=1,
                                team_name='CKM 1',
                            ),
                        },
                    ),
                ),
                source=MessageSource.SOURCE_DUMMY,
                created_at=1679944690.8801994,
                updated_at=1679944690.8801994,
                decoder=MessageDecoder.ACTION,
                error_description='This is a sample description',
                error_traceback='Sample error trace'),
        ],
    )
    def test_encode_decode(self, message: Message) -> None:
        """Test decoding message."""
        encoded_message = message.encode()
        decoded_message: Message = Message.decode(encoded_message)

        assert decoded_message.competition_code == message.competition_code
        assert decoded_message.data == message.data
        assert decoded_message.source == message.source
        assert decoded_message.created_at == message.created_at
        assert decoded_message.updated_at == message.updated_at
        assert decoded_message.decoder == message.decoder
        assert decoded_message.error_description == message.error_description
        assert decoded_message.error_traceback == message.error_traceback

    def test_decode_with_missing_key(self) -> None:
        """Test decoding a message with a missing key."""
        encoded_message = json.dumps({
            'competition_code': 'sample-code',
            'data': 'Hello, World!',
            'source': MessageSource.SOURCE_DUMMY.value,
            'created_at': datetime.utcnow().timestamp(),
        })
        with pytest.raises(Exception) as e_info:
            _ = Message.decode(encoded_message)
        exception: Exception = e_info.value
        assert str(exception).startswith('Key "updated_at" does not exist in:')

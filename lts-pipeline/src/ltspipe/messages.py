from datetime import datetime
import json
from pydantic import Field, SerializeAsAny
from typing import Any, Optional, Union

from ltspipe.data.base import EnumBase, BaseModel
from ltspipe.data.actions import Action
from ltspipe.data.notifications import Notification
from ltspipe.exceptions import LtsError


class MessageSource(EnumBase):
    """Enumeration of sources of messages."""

    SOURCE_DUMMY = 'dummy'
    SOURCE_WS_LISTENER = 'ws-listener'


class MessageDecoder(EnumBase):
    """Decoders of message data."""

    ACTION = 'action'
    NOTIFICATION = 'notification'


class Message(BaseModel):
    """
    Basic unit of information that the steps share between them.

    Attributes:
        competition_code (str): Verbose code to identify the competition.
        data (Any): Data of the message.
        source (MessageSource): The source message.
        created_at (float): Timestamp when the message was created.
        updated_at (float): Timestamp of last time the message was updated.
        decoder (MessageDecoder | None): If necessary, provide the decoder of
            the message data.
        error_description (str | None): If there was any error with this
            message, this field has the error description.
        error_traceback (str | None): If there was any error with this
            message, this field has the traceback.
    """

    competition_code: str
    data: SerializeAsAny[Any]
    source: MessageSource
    created_at: float
    updated_at: float
    decoder: Optional[MessageDecoder] = Field(default=None)
    error_description: Optional[str] = Field(default=None)
    error_traceback: Optional[str] = Field(default=None)

    def has_error(self) -> bool:
        """Return true if the message contains an error description."""
        return (self.error_description is not None
                or self.error_traceback is not None)

    def updated(self) -> None:
        """Change 'updated_at' to the current timestamp."""
        self.updated_at = datetime.utcnow().timestamp()

    def encode(self) -> str:
        """Encode the message as a string."""
        data = self.model_dump()
        return json.dumps(data)

    def __str__(self) -> str:
        """Encode the message as a string."""
        return self.encode()

    @staticmethod
    def decode(encoded: Union[str, bytes, bytearray]) -> Any:
        """Decode a string-format message."""
        msg = json.loads(encoded)
        competition_code = Message.__get_by_key(msg, 'competition_code')
        raw_data: Any = Message.__get_by_key(msg, 'data')
        str_source = Message.__get_by_key(msg, 'source')
        created_at = Message.__get_by_key(msg, 'created_at')
        updated_at = Message.__get_by_key(msg, 'updated_at')
        raw_decoder = Message.__get_by_key(msg, 'decoder')
        error_description = Message.__get_by_key(
            msg, 'error_description', required=False)
        error_traceback = Message.__get_by_key(
            msg, 'error_traceback', required=False)

        decoder = (None if raw_decoder is None
                   else MessageDecoder.value_of(raw_decoder))
        return Message(
            competition_code=competition_code,
            data=Message.__decode_data(decoder, raw_data),
            source=MessageSource.value_of(str_source),
            created_at=created_at,
            updated_at=updated_at,
            decoder=decoder,
            error_description=error_description,
            error_traceback=error_traceback,
        )

    @staticmethod
    def __decode_data(
            decoder: Optional[MessageDecoder],
            raw_data: Any) -> Any:
        """Decode data and transform it into a model if possible."""
        if decoder is None:
            return raw_data
        elif isinstance(raw_data, dict):
            if decoder == MessageDecoder.ACTION:
                return Action.from_dict(raw_data)
            elif decoder == MessageDecoder.NOTIFICATION:
                return Notification.from_dict(raw_data)

        raise LtsError(f'Unknown data format: {raw_data}')

    @staticmethod
    def __get_by_key(data: dict, key: str, required: bool = True) -> Any:
        """Retrieve 'key' from data."""
        if key in data:
            return data[key]
        elif required:
            raise LtsError(f'Key "{key}" does not exist in: {data}')
        else:
            return None

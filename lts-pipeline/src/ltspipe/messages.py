from datetime import datetime
import json
from pydantic import Field
from typing import Any, Optional, Union

from ltspipe.base import EnumBase, BaseModel


class MessageSource(EnumBase):
    """Enumeration of sources of messages."""

    SOURCE_DUMMY = 'dummy'
    SOURCE_WS_LISTENER = 'ws-listener'


class Message(BaseModel):
    """
    Basic unit of information that the steps share between them.

    Attributes:
        competition_code (str): Verbose code to identify the competition.
        data (Any): Data of the message.
        source (MessageSource): The source message.
        created_at (float): Timestamp when the message was created.
        updated_at (float): Timestamp of last time the message was updated.
        error_description (str | None): If there was any error with this
            message, this field has the error description.
        error_traceback (str | None): If there was any error with this
            message, this field has the traceback.
    """

    competition_code: str
    data: Any
    source: MessageSource
    created_at: float
    updated_at: float
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
        data = self.dict()
        return json.dumps(data)

    def __str__(self) -> str:
        """Encode the message as a string."""
        return self.encode()

    @staticmethod
    def decode(encoded: Union[str, bytes, bytearray]) -> Any:
        """Decode a string-format message."""
        msg = json.loads(encoded)
        competition_code = Message.__get_by_key(msg, 'competition_code')
        data = Message.__get_by_key(msg, 'data')
        str_source = Message.__get_by_key(msg, 'source')
        created_at = Message.__get_by_key(msg, 'created_at')
        updated_at = Message.__get_by_key(msg, 'updated_at')
        error_description = Message.__get_by_key(
            msg, 'error_description', required=False)
        error_traceback = Message.__get_by_key(
            msg, 'error_traceback', required=False)
        return Message(
            competition_code=competition_code,
            data=data,
            source=MessageSource.value_of(str_source),
            created_at=created_at,
            updated_at=updated_at,
            error_description=error_description,
            error_traceback=error_traceback,
        )

    @staticmethod
    def __get_by_key(data: dict, key: str, required: bool = True) -> Any:
        """Retrieve 'key' from data."""
        if key in data:
            return data[key]
        elif required:
            raise Exception(f'Key "{key}" does not exist in: {data}')
        else:
            return None

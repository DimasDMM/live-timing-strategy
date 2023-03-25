from datetime import datetime
from enum import Enum
import json
from typing import Any, Union


class MessageSource(Enum):
    """Enumeration of sources of messages."""

    SOURCE_DUMMY = 'dummy'
    SOURCE_WS_LISTENER = 'ws-listener'

    def __eq__(self, other: Any) -> bool:
        """Compare enumeration to other objects and strings."""
        if self.__class__ is other.__class__:
            return self.value == other.value
        elif isinstance(other, str):
            return self.value == other
        return False

    def __hash__(self) -> int:
        """Build hash of current instance."""
        return hash(self.value)

    @classmethod
    def value_of(cls: Any, value: Any) -> Any:
        """Build source message from a given value."""
        for k, v in cls.__members__.items():
            if MessageSource[k] == value:
                return v
        raise ValueError(f'"{cls.__name__}" enum not found for "{value}".')


class Message:
    """Basic unit of information that the steps share between them."""

    def __init__(
            self,
            data: Any,
            source: MessageSource,
            created_at: float,
            updated_at: float) -> None:
        """
        Construct.

        Params:
            data (Any): data of the message.
            source (MessageSource): the source message.
            created_at (float): timestamp when the message was created.
            updated_at (float): timestamp of last time the message was updated.
        """
        self._data = data
        self._source = source
        self._created_at = created_at
        self._updated_at = updated_at

    def get_data(self) -> Any:
        """Get data of the message."""
        return self._data

    def get_source(self) -> MessageSource:
        """Get source of the message."""
        return self._source

    def get_created_at(self) -> float:
        """
        Get timestamp when the message was created.
        """
        return self._created_at

    def get_updated_at(self) -> float:
        """
        Get timestamp of last time the message was updated.
        """
        return self._updated_at

    def updated(self) -> None:
        """
        Change 'updated_at' to the current timestamp.
        """
        self._updated_at = datetime.utcnow().timestamp()

    def encode(self) -> str:
        """Encode the message as a string."""
        data = {
            'data': self.get_data(),
            'source': self.get_source().value,
            'created_at': self.get_created_at(),
            'updated_at': self.get_updated_at(),
        }
        return json.dumps(data)

    def __str__(self) -> str:
        """Encode the message as a string."""
        return self.encode()

    @staticmethod
    def decode(encoded: Union[str, bytes, bytearray]) -> Any:
        """Decode a string-format message."""
        msg = json.loads(encoded)
        data = Message.__get_by_key(msg, 'data')
        str_source = Message.__get_by_key(msg, 'source')
        created_at = Message.__get_by_key(msg, 'created_at')
        updated_at = Message.__get_by_key(msg, 'updated_at')
        return Message(
            data=data,
            source=MessageSource.value_of(str_source),
            created_at=created_at,
            updated_at=updated_at,
        )

    @staticmethod
    def __get_by_key(data: dict, key: str) -> Any:
        """Retrieve 'key' from data."""
        if key in data:
            return data[key]
        raise Exception(f'Key "{key}" does not exist in: {data}')

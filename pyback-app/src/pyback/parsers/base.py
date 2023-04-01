import abc
from typing import Optional

from pyback.messages import Message


class Parser(abc.ABC):
    """
    Unit of data parsing.
    """

    @abc.abstractmethod
    def parse(self, msg: Message) -> Optional[Message]:
        """
        Analyse and/or parse a given message.

        Params:
            msg (Message): Message to parse.

        Returns:
            Optional[Message]: transformed message (or the original message
                if no transformation is needed).
        """
        raise NotImplementedError

    def __call__(self, msg: Message) -> Optional[Message]:
        """Forward to method Parser.parse()."""
        return self.parse(msg)

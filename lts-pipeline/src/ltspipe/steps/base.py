import abc
from typing import Any, List

from ltspipe.messages import Message


class BaseStep(abc.ABC):
    """
    Unit of message processing.
    """

    @abc.abstractmethod
    def get_children(self) -> List[Any]:
        """Return list of children steps to this one."""
        raise NotImplementedError


class StartStep(BaseStep, abc.ABC):
    """
    Unit to start processing messages.
    """

    @abc.abstractmethod
    def start_step(self) -> None:
        """Start processing messages."""
        raise NotImplementedError


class MidStep(BaseStep, abc.ABC):
    """
    Unit to process messages from a previous step.
    """

    @abc.abstractmethod
    def run_step(self, msg: Message) -> None:
        """Process messages."""
        raise NotImplementedError

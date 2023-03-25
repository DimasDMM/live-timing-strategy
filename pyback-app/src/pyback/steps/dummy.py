from datetime import datetime
import time
from typing import Any, List

from pyback.messages import Message, MessageSource
from pyback.steps.base import StartStep, MidStep


class DummyStartStep(StartStep):
    """Step to generate dummy messages for debugging purposes."""

    def __init__(
            self,
            next_step: MidStep,
            n_messages: int = 100) -> None:
        """
        Construct.

        Params:
            next_step (MidStep): The next step to apply to the message.
            n_messages (int): Number of messages to generate.
        """
        self._next_step = next_step
        self._n_messages = n_messages

    def get_children(self) -> List[Any]:
        """Return list of children steps to this one."""
        return [self._next_step] + self._next_step.get_children()

    def start_step(self) -> None:
        """Start generating dummy messages."""
        for i in range(self._n_messages):
            msg = Message(
                data={'counter': i},
                source=MessageSource.SOURCE_DUMMY,
                created_at=datetime.utcnow().timestamp(),
                updated_at=datetime.utcnow().timestamp(),
            )
            self._next_step.run_step(msg)
            time.sleep(0.5)

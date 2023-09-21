from datetime import datetime
import time
from typing import Any, List, Optional

from ltspipe.messages import Message, MessageSource
from ltspipe.steps.base import StartStep, MidStep


class DummyStartStep(StartStep):
    """Step to generate dummy messages for debugging purposes."""

    DUMMY_CODE = 'dummy-code'

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

    def get_children(self) -> List[MidStep]:
        """Return list of children steps to this one."""
        return [self._next_step] + self._next_step.get_children()

    def start_step(self) -> None:
        """Start generating dummy messages."""
        for i in range(self._n_messages):
            msg = Message(
                competition_code=DummyStartStep.DUMMY_CODE,
                data={'counter': i},
                source=MessageSource.SOURCE_DUMMY,
                created_at=datetime.utcnow().timestamp(),
                updated_at=datetime.utcnow().timestamp(),
            )
            self._next_step.run_step(msg)
            time.sleep(0.5)


class NullStep(MidStep):
    """Step that does nothing."""

    def __init__(self, next_step: Optional[MidStep] = None) -> None:
        """
        Construct.

        Params:
            next_step (MidStep | None): Optionally, apply another step to the
                message.
        """
        self._next_step = next_step

    def get_children(self) -> List[Any]:
        """Return list of children steps to this one."""
        if self._next_step is None:
            return []
        else:
            return [self._next_step] + self._next_step.get_children()

    def run_step(self, msg: Message) -> None:
        """Run step."""
        if self._next_step is not None:
            msg.updated()
            self._next_step.run_step(msg)

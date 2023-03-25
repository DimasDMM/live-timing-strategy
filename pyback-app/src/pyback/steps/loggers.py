import logging
from typing import Any, List, Optional

from pyback.messages import Message
from pyback.steps.base import MidStep


class LogInfoStep(MidStep):
    """Step to display a message with the level 'info'."""

    def __init__(
            self,
            logger: logging.Logger,
            next_step: Optional[MidStep] = None) -> None:
        """
        Construct.

        Params:
            logger (logging.Logger): Logger instance to display messages in
                the step.
        """
        self._logger = logger
        self._next_step = next_step

    def get_children(self) -> List[Any]:
        """Return list of children steps to this one."""
        if self._next_step is None:
            return []
        else:
            return [self._next_step] + self._next_step.get_children()

    def run_step(self, msg: Message) -> None:
        """Display a message."""
        self._logger.info(str(msg))
        if self._next_step is not None:
            self._next_step.run_step(msg)

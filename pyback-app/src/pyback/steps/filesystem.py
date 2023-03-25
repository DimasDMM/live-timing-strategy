import logging
import os
import time
from typing import Any, List, Optional

from pyback.messages import Message
from pyback.steps.base import MidStep


class FileStorageStep(MidStep):
    """Step to store a message in the file system."""

    def __init__(
            self,
            logger: logging.Logger,
            output_path: str,
            next_step: Optional[MidStep] = None) -> None:
        """
        Construct.

        Params:
            logger (logging.Logger): Logger instance to display information.
            output_path (str): Path to store messages in files.
            next_step (MidStep): The next step to apply to the message.
        """
        self._logger = logger
        self._output_path = output_path
        self._next_step = next_step

    def get_children(self) -> List[Any]:
        """Return list of children steps to this one."""
        if self._next_step is None:
            return []
        else:
            return [self._next_step] + self._next_step.get_children()

    def run_step(self, msg: Message) -> None:
        """Save a message in the file system."""
        file_name = f'{time.time()}.raw.txt'
        file_path = os.path.join(self._output_path, file_name)
        self._logger.debug(f'Save message into "{file_path}"...')
        with open(file_path, 'w') as fp:
            fp.write(str(msg))

        if self._next_step is not None:
            self._next_step.run_step(msg)

import logging
import os
import time
from typing import Any, List, Optional

from ltspipe.messages import Message
from ltspipe.steps.base import MidStep


class MessageStorageStep(MidStep):
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
            next_step (MidStep | None): Optionally, apply another step to the
                message.
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
        file_name = f'{time.time()}.msg.txt'
        file_path = os.path.join(self._output_path, file_name)
        self._logger.debug(f'Save message into "{file_path}"...')
        with open(file_path, 'w') as fp:
            fp.write(str(msg))

        if self._next_step is not None:
            msg.updated()
            self._next_step.run_step(msg)


class RawStorageStep(MidStep):
    """Step to store the raw data in the file system."""

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
            next_step (MidStep | None): Optionally, apply another step to the
                message.
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
            fp.write(str(msg.data))

        if self._next_step is not None:
            msg.updated()
            self._next_step.run_step(msg)

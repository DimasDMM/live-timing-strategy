from logging import Logger
from typing import Any, Dict, List, Optional

from ltspipe.data.enum import FlagName
from ltspipe.messages import Message
from ltspipe.steps.base import MidStep


class QueueDistributorStep(MidStep):
    """
    Queue messages if the flag 'flag_name' is enabled.

    This class should receive a boolean and a queue (FIFO). Whenever the boolean
    is set to True, all the messages will end up in the queue. Note that this
    class will not clear the queue.
    """

    def __init__(
            self,
            logger: Logger,
            flags: Dict[str, Dict[FlagName, Any]],
            flag_name: FlagName,
            queue: Dict[str, List[Message]],
            next_step: MidStep) -> None:
        """Construct."""
        self._logger = logger
        self._flags = flags
        self._flag_name = flag_name
        self._queue = queue
        self._next_step = next_step

    def get_children(self) -> List[Any]:
        """Return list of children steps to this one."""
        return [self._next_step] + self._next_step.get_children()

    def run_step(self, msg: Message) -> None:
        """Run step."""
        code = msg.competition_code
        wait_status: bool = False
        if code in self._flags:
            wait_status = self._flags[code].get(self._flag_name, False)

        if wait_status:
            size = len(self._queue.get(code, [])) + 1
            self._logger.info(f'Add message to queue (current size: {size}).')
            if code not in self._queue:
                self._queue[code] = []
            self._queue[code].append(msg)
        else:
            self._logger.debug('Skip queue.')
            msg.updated()
            self._next_step.run_step(msg)


class QueueForwardStep(MidStep):
    """Step to forward all the messages that a queue contains."""

    def __init__(
            self,
            logger: Logger,
            queue: Dict[str, List[Message]],
            queue_step: MidStep,
            next_step: Optional[MidStep] = None) -> None:
        """
        Construct.

        Params:
            logger (logging.Logger): Logger instance to display information.
            queue (Dict[str, List[Message]]): queue (FIFO) containing messages.
            queue_step (MidStep): Step to forward all the content of the queue.
            next_step (MidStep | None): If given, it forwards the message
                received by 'run_step()' to this other step.
        """
        self._logger = logger
        self._queue = queue
        self._queue_step = queue_step
        self._next_step = next_step

    def get_children(self) -> List[Any]:
        """Return list of children steps to this one."""
        children = [self._queue_step] + self._queue_step.get_children()
        if self._next_step is not None:
            children += [self._next_step] + self._next_step.get_children()
        return children

    def run_step(self, msg: Message) -> None:
        """
        Run step.

        Forward all messages in queue.

        Note that the 'msg' is forwarded to 'next_step' and it has nothing to do
        with the content of the queue.
        """
        code = msg.competition_code
        if code in self._queue:
            while len(self._queue[code]) > 0:
                queue_msg = self._queue[code].pop(0)
                queue_msg.updated()
                self._queue_step.run_step(queue_msg)

        if self._next_step is not None:
            msg.updated()
            self._next_step.run_step(msg)

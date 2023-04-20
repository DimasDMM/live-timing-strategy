from logging import Logger
from typing import Any, Dict, List, Optional

from ltspipe.data.enum import FlagName
from ltspipe.messages import Message
from ltspipe.steps.base import MidStep


class FlagModifierStep(MidStep):
    """
    Set the flag to a specific value when it receives a message.
    """

    def __init__(
            self,
            logger: Logger,
            flags: Dict[str, Dict[FlagName, Any]],
            flag_name: FlagName,
            flag_value: Any,
            next_step: Optional[MidStep] = None) -> None:
        """
        Construct.

        Params:
            logger (logging.Logger): Logger instance to display information.
            flags (Dict[str, Dict[FlagName, Any]]): Dictionary of flags.
            flag_name (FlagName): Name of the value to set.
            flag_value (Any): Value to set.
            next_step (MidStep | None): Next step.
        """
        self._logger = logger
        self._flags = flags
        self._flag_name = flag_name
        self._flag_value = flag_value
        self._next_step = next_step

    def get_children(self) -> List[Any]:
        """Return list of children steps to this one."""
        if self._next_step is None:
            return []
        else:
            return [self._next_step] + self._next_step.get_children()

    def run_step(self, msg: Message) -> None:
        """Change the value of the flag."""
        code = msg.competition_code
        if code not in self._flags:
            self._flags[code] = {}
        self._flags[code][self._flag_name] = self._flag_value

        if self._next_step is not None:
            msg.updated()
            self._next_step.run_step(msg)

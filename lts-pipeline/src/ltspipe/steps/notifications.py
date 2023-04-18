from logging import Logger
from typing import Any, Dict, List, Optional

from ltspipe.data.enum import (
    ActionType,
    FlagName,
    NotificationType,
)
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


class NotificationMapperStep(MidStep):
    """
    Detect if the message is a notification and forward it.
    """

    def __init__(
            self,
            logger: Logger,
            map_notification: Dict[NotificationType, MidStep],
            on_other: Optional[MidStep] = None) -> None:
        """
        Construct.

        Params:
            logger (logging.Logger): Logger instance to display information.
            map_notification (Dict[NotificationType, MidStep]): Map each type of
                notification to a step.
            on_other (MidStep): Next step when it is other kind of data.
        """
        self._logger = logger
        self._map_notification = map_notification
        self._on_other = on_other

    def get_children(self) -> List[Any]:
        """Return list of children steps to this one."""
        children = []
        if self._on_other is not None:
            children += [self._on_other] + self._on_other.get_children()
        for _, step in self._map_notification.items():
            children += [step] + step.get_children()
        return children

    def run_step(self, msg: Message) -> None:
        """Add message to queue or continue to the next step."""
        type = self._get_notification_type(msg)
        if type is not None and type in self._map_notification:
            self._logger.info(f'Notification: {type}.')
            msg.updated()
            self._map_notification[type].run_step(msg)
        elif self._on_other is not None:
            msg.updated()
            self._on_other.run_step(msg)

    def _get_notification_type(
            self, msg: Message) -> Optional[NotificationType]:
        """Return the notification type if the message is a notification."""
        if 'type' in msg.data and msg.data['type'] == ActionType.NOTIFICATION:
            return msg.data['data'] if 'data' in msg.data else None
        return None

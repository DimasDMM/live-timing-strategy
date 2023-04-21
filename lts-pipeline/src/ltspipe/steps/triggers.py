from datetime import datetime
from logging import Logger
import re
from typing import Any, List, Optional

from ltspipe.data.actions import Action, ActionType
from ltspipe.data.notifications import Notification, NotificationType
from ltspipe.messages import Message, MessageDecoder, MessageSource
from ltspipe.steps.base import MidStep


class ActionInitTriggerStep(MidStep):
    """
    Detect if the message is about initialization and create a notification.
    """

    def __init__(
            self,
            logger: Logger,
            on_init_trigger: Optional[MidStep] = None,
            on_init: Optional[MidStep] = None,
            on_other: Optional[MidStep] = None) -> None:
        """
        Construct.

        Params:
            logger (logging.Logger): Logger instance to display information.
            on_init_trigger (MidStep | None): Step to pass the notification.
            on_init (MidStep | None): Next step when it is initializer action.
            on_other (MidStep | None): Next step when it is other kind of data.
        """
        self._logger = logger
        self._on_init_trigger = on_init_trigger
        self._on_init = on_init
        self._on_other = on_other

    def get_children(self) -> List[Any]:
        """Return list of children steps to this one."""
        children = []
        if self._on_init is not None:
            children += [self._on_init] + self._on_init.get_children()
        if self._on_other is not None:
            children += [self._on_other] + self._on_other.get_children()
        if self._on_init_trigger is not None:
            children += [self._on_init_trigger]
            children += self._on_init_trigger.get_children()
        return children

    def run_step(self, msg: Message) -> None:
        """Add message to queue or continue to the next step."""
        type = self._get_action_type(msg)
        if type is not None and type == ActionType.INITIALIZE:
            self._do_notification(
                competition_code=msg.competition_code,
                source=msg.source,
            )
            if self._on_init is not None:
                msg.updated()
                self._on_init.run_step(msg)
        elif self._on_other is not None:
            msg.updated()
            self._on_other.run_step(msg)

    def _get_action_type(
            self, msg: Message) -> Optional[ActionType]:
        """Return the action type if the message is a action."""
        if isinstance(msg.data, Action):
            return msg.data.type
        return None

    def _do_notification(
            self,
            competition_code: str,
            source: MessageSource) -> None:
        """Notify that there was initializer data."""
        if self._on_init_trigger is None:
            return

        notification = Message(
            competition_code=competition_code,
            data=Notification(
                type=NotificationType.INIT_FINISHED,
            ),
            source=source,
            decoder=MessageDecoder.NOTIFICATION,
            created_at=datetime.utcnow().timestamp(),
            updated_at=datetime.utcnow().timestamp(),
        )
        self._on_init_trigger.run_step(notification)


class WsInitTriggerStep(MidStep):
    """Detect if the given raw message is initializer data."""

    def __init__(
            self,
            logger: Logger,
            on_init_trigger: Optional[MidStep] = None,
            on_init: Optional[MidStep] = None,
            on_other: Optional[MidStep] = None) -> None:
        """
        Construct.

        Params:
            logger (logging.Logger): Logger instance to display information.
            on_init_trigger (MidStep | None): Step to pass the notification.
            on_init (MidStep | None): Next step when it is initializer data.
            on_other (MidStep | None): Next step when it is other kind of data.
        """
        self._logger = logger
        self._on_init_trigger = on_init_trigger
        self._on_init = on_init
        self._on_other = on_other

    def get_children(self) -> List[Any]:
        """Return list of children steps to this one."""
        children = []
        if self._on_init is not None:
            children += [self._on_init] + self._on_init.get_children()
        if self._on_other is not None:
            children += [self._on_other] + self._on_other.get_children()
        if self._on_init_trigger is not None:
            children += [self._on_init_trigger]
            children += self._on_init_trigger.get_children()
        return children

    def run_step(self, msg: Message) -> None:
        """Add message to queue or continue to the next step."""
        if self._is_init_data(msg):
            self._logger.info('Initializer data detected.')
            self._do_notification(
                competition_code=msg.competition_code,
                source=msg.source,
            )
            if self._on_init is not None:
                msg.updated()
                self._on_init.run_step(msg)
        elif self._on_other is not None:
            msg.updated()
            self._on_other.run_step(msg)

    def _do_notification(
            self,
            competition_code: str,
            source: MessageSource) -> None:
        """Notify that there was initializer data."""
        if self._on_init_trigger is None:
            return

        notification = Message(
            competition_code=competition_code,
            data=Notification(
                type=NotificationType.INIT_ONGOING,
            ),
            source=source,
            decoder=MessageDecoder.NOTIFICATION,
            created_at=datetime.utcnow().timestamp(),
            updated_at=datetime.utcnow().timestamp(),
        )
        self._on_init_trigger.run_step(notification)

    def _is_init_data(self, msg: Message) -> bool:
        """Detect if it is initializer data."""
        return re.match(r'^init\|', msg.data) is not None

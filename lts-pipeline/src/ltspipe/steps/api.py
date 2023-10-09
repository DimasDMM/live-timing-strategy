from datetime import datetime
from logging import Logger
from typing import Any, Dict, List, Optional

from ltspipe.api.handlers.base import ApiHandler
from ltspipe.api.competitions_base import build_competition_info
from ltspipe.data.actions import Action, ActionType
from ltspipe.data.auth import AuthData
from ltspipe.data.competitions import CompetitionInfo
from ltspipe.data.notifications import Notification
from ltspipe.messages import Message, MessageDecoder, MessageSource
from ltspipe.steps.base import MidStep


class ApiActionStep(MidStep):
    """Do an action with the API REST."""

    def __init__(
            self,
            logger: Logger,
            api_lts: str,
            info: CompetitionInfo,
            action_handlers: Dict[ActionType, ApiHandler],
            notification_step: Optional[MidStep],
            next_step: Optional[MidStep] = None) -> None:
        """
        Construct.

        Params:
            logger (logging.Logger): Logger instance to display information.
            api_lts (str): URI of API REST.
            info (CompetitionInfo): Storage of competition info.
            action_handlers (Dict[ActionType, ApiHandler]): Handler for each
                type of action.
            notification_step (MidStep | None): Step to send a notification when
                a handler is applied.
            next_step (MidStep | None): Next step.
        """
        self._logger = logger
        self._api_lts = api_lts
        self._info = info
        self._action_handlers = action_handlers
        self._notification_step = notification_step
        self._next_step = next_step

    def get_children(self) -> List[Any]:
        """Return list of children steps to this one."""
        children = []
        if self._next_step is not None:
            children += [self._next_step] + self._next_step.get_children()
        if self._notification_step is not None:
            children += [self._notification_step]
            children += self._notification_step.get_children()
        return children

    def run_step(self, msg: Message) -> None:
        """Run step."""
        if isinstance(msg.data, Action):
            action = msg.data
            handler = self._action_handlers.get(action.type, None)
            if handler is not None:
                notification = handler.handle(action.data)
                self._forward_notification(
                    msg.competition_code,
                    msg.source,
                    notification)

        if self._next_step is not None:
            self._next_step.run_step(msg)

    def _forward_notification(
            self,
            competition_code: str,
            source: MessageSource,
            notification: Optional[Notification]) -> None:
        """Forward the notification to another step in a message."""
        if notification is None or self._notification_step is None:
            return

        message = Message(
            competition_code=competition_code,
            data=notification,
            source=source,
            decoder=MessageDecoder.NOTIFICATION,
            created_at=datetime.utcnow().timestamp(),
            updated_at=datetime.utcnow().timestamp(),
        )
        self._notification_step.run_step(message)


class CompetitionInfoRefreshStep(MidStep):
    """Retrieve the info of the competition."""

    def __init__(
            self,
            logger: Logger,
            api_lts: str,
            auth_data: AuthData,
            info: CompetitionInfo,
            next_step: Optional[MidStep] = None) -> None:
        """
        Construct.

        Params:
            logger (logging.Logger): Logger instance to display information.
            api_lts (str): URI of API REST.
            auth_data (AuthData): Authentication data.
            info (CompetitionInfo): Storage of competition info.
            next_step (MidStep | None): Next step.
        """
        self._logger = logger
        self._api_lts = api_lts.strip('/')
        self._auth_data = auth_data
        self._info = info
        self._next_step = next_step

    def get_children(self) -> List[Any]:
        """Return list of children steps to this one."""
        if self._next_step is None:
            return []
        else:
            return [self._next_step] + self._next_step.get_children()

    def run_step(self, msg: Message) -> None:
        """Run step."""
        self._refresh_competition_info(msg.competition_code)
        if self._next_step is not None:
            self._next_step.run_step(msg)

    def _refresh_competition_info(self, competition_code: str) -> None:
        """Refresh competition info."""
        self._logger.debug(
            f'Refresh competition info of {competition_code}...')
        new_info = build_competition_info(
            self._api_lts,
            bearer=self._auth_data.bearer,
            competition_code=competition_code)
        if new_info is None:
            raise Exception(
                f'Competition does not exist: {competition_code}')

        self._info.id = new_info.id
        self._info.teams = new_info.teams
        self._info.drivers = new_info.drivers
        self._info.parser_settings = new_info.parser_settings

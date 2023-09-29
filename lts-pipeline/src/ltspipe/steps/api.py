from datetime import datetime
from logging import Logger
from typing import Any, Dict, List, Optional

from ltspipe.api.handlers.base import ApiHandler
from ltspipe.api.competitions_base import build_competition_info
from ltspipe.data.actions import Action, ActionType
from ltspipe.data.auth import AuthData
from ltspipe.data.competitions import CompetitionInfo
from ltspipe.data.enum import FlagName
from ltspipe.data.notifications import Notification
from ltspipe.messages import Message, MessageDecoder, MessageSource
from ltspipe.steps.base import MidStep


class ApiActionStep(MidStep):
    """Do an action with the API REST."""

    def __init__(
            self,
            logger: Logger,
            api_lts: str,
            competitions: Dict[str, CompetitionInfo],
            action_handlers: Dict[ActionType, ApiHandler],
            notification_step: Optional[MidStep],
            next_step: Optional[MidStep] = None) -> None:
        """
        Construct.

        Params:
            logger (logging.Logger): Logger instance to display information.
            api_lts (str): URI of API REST.
            competitions (Dict[str, CompetitionInfo]): Storage of
                competitions info.
            action_handlers (Dict[ActionType, ApiHandler]): Handler for each
                type of action.
            notification_step (MidStep | None): Step to send a notification when
                a handler is applied.
            next_step (MidStep | None): Next step.
        """
        self._logger = logger
        self._api_lts = api_lts
        self._competitions = competitions
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
            if msg.competition_code not in self._competitions:
                raise Exception(
                    f'Unknown competition with code {msg.competition_code}.')

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


class CompetitionInfoInitStep(MidStep):
    """Retrieve the info of the competition."""

    def __init__(
            self,
            logger: Logger,
            api_lts: str,
            auth_data: AuthData,
            competitions: Dict[str, CompetitionInfo],
            flags: Dict[str, Dict[FlagName, Any]],
            force_update: bool = False,
            next_step: Optional[MidStep] = None) -> None:
        """
        Construct.

        Params:
            logger (logging.Logger): Logger instance to display information.
            api_lts (str): URI of API REST.
            auth_data (AuthData): Authentication data.
            competitions (Dict[str, CompetitionInfo]): Storage of
                competitions info.
            flags (Dict[str, Dict[FlagName, Any]]): dictionary of flags.
                If the flag 'FlagName.REFRESH_COMPETITION' is set to true, it
                will refresh the information about the competition. The value is
                ignored if 'force_update' is set to True.
            force_update (bool): If the info of a competition is already set,
                it forces to get again its information. If this value is set to
                True, it ignores the value from the flag.
            next_step (MidStep | None): Next step.
        """
        self._logger = logger
        self._api_lts = api_lts.strip('/')
        self._auth_data = auth_data
        self._competitions = competitions
        self._flags = flags
        self._flag_name = FlagName.REFRESH_COMPETITION
        self._force_update = force_update
        self._next_step = next_step

    def get_children(self) -> List[Any]:
        """Return list of children steps to this one."""
        if self._next_step is None:
            return []
        else:
            return [self._next_step] + self._next_step.get_children()

    def run_step(self, msg: Message) -> None:
        """Run step."""
        self._init_competition_info(msg.competition_code)
        if self._next_step is not None:
            self._next_step.run_step(msg)

    def _init_competition_info(self, competition_code: str) -> None:
        """Initialize competition info."""
        if ((self._flag_name in self._flags and self._flags[self._flag_name])
                or self._force_update
                or competition_code not in self._competitions):
            self._logger.debug(
                f'Init competition info of {competition_code}...')
            info = build_competition_info(
                self._api_lts,
                bearer=self._auth_data.bearer,
                competition_code=competition_code)
            if info is not None:
                self._competitions[competition_code] = info

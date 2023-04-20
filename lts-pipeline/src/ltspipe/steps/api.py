from logging import Logger
from typing import Any, Dict, List, Optional

from ltspipe.api.handlers import ApiHandler
from ltspipe.api.competitions_base import (
    init_competition_info,
)
from ltspipe.data.actions import Action, ActionType
from ltspipe.data.competitions import CompetitionInfo
from ltspipe.messages import Message
from ltspipe.steps.base import MidStep


class ApiActionStep(MidStep):
    """Do an action with the API REST."""

    def __init__(
            self,
            logger: Logger,
            api_lts: str,
            competitions: Dict[str, CompetitionInfo],
            action_handlers: Dict[ActionType, ApiHandler],
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
            next_step (MidStep | None): Next step.
        """
        self._logger = logger
        self._api_lts = api_lts
        self._competitions = competitions
        self._action_handlers = action_handlers
        self._next_step = next_step

    def get_children(self) -> List[Any]:
        """Return list of children steps to this one."""
        if self._next_step is not None:
            return [self._next_step] + self._next_step.get_children()
        return []

    def run_step(self, msg: Message) -> None:
        """Do an action with the API REST."""
        if isinstance(msg.data, Action):
            if msg.competition_code not in self._competitions:
                raise Exception(
                    f'Unknown competition with code {msg.competition_code}.')

            action = msg.data
            handler = self._action_handlers.get(action.type, None)
            if handler is not None:
                handler.handle(action.data)

        if self._next_step is not None:
            self._next_step.run_step(msg)


class CompetitionInfoInitStep(MidStep):
    """Retrieve the info of the competition."""

    def __init__(
            self,
            logger: Logger,
            api_lts: str,
            competitions: Dict[str, CompetitionInfo],
            force_update: bool = True,
            next_step: Optional[MidStep] = None) -> None:
        """
        Construct.

        Params:
            logger (logging.Logger): Logger instance to display information.
            api_lts (str): URI of API REST.
            competitions (Dict[str, CompetitionInfo]): Storage of
                competitions info.
            force_update (bool): If the info of a competition is already set,
                it forces to get again its information.
            next_step (MidStep | None): Next step.
        """
        self._logger = logger
        self._api_lts = api_lts.strip('/')
        self._competitions = competitions
        self._force_update = force_update
        self._next_step = next_step

    def get_children(self) -> List[Any]:
        """Return list of children steps to this one."""
        if self._next_step is None:
            return []
        else:
            return [self._next_step] + self._next_step.get_children()

    def run_step(self, msg: Message) -> None:
        """Update parsers settings of the competition."""
        self._init_competition_info(msg.competition_code)
        if self._next_step is not None:
            self._next_step.run_step(msg)

    def _init_competition_info(self, competition_code: str) -> None:
        """Initialize competition info."""
        if self._force_update or competition_code not in self._competitions:
            info = init_competition_info(
                self._api_lts, competition_code)
            self._competitions[competition_code] = info

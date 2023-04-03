import logging
from typing import Any, List, Optional

from ltspipe.data.actions import Action
from ltspipe.parsers.base import Parser
from ltspipe.messages import Message
from ltspipe.steps.base import MidStep


class ParsersStep(MidStep):
    """Step to parse the initial info from a websocket."""

    def __init__(
            self,
            logger: logging.Logger,
            parsers: List[Parser],
            stop_on_first: bool = True,
            on_parsed: Optional[MidStep] = None,
            on_unknown: Optional[MidStep] = None,
            on_error: Optional[MidStep] = None) -> None:
        """
        Construct.

        Params:
            logger (logging.Logger): Logger instance to display information.
            parsers (List[Parser]): List of parsers to apply.
            stop_on_first (bool): Stop parsing after one parser has returned
                some actions.
            on_parsed (MidStep | None): Optionally, apply another step to the
                message when the data is parsed.
            on_unknown (MidStep | None): Optionally, apply another step to the
                message if the current parser could not detect the format.
            on_error (MidStep | None): Optionally, apply another step to the
                message if the current parser had some error parsing the data.
        """
        self._logger = logger
        self._parsers = parsers
        self._stop_on_first = stop_on_first
        self._on_parsed = on_parsed
        self._on_unknown = on_unknown
        self._on_error = on_error

    def get_children(self) -> List[Any]:
        """Return list of children steps to this one."""
        children = []
        if self._on_parsed is not None:
            children += [self._on_parsed] + self._on_parsed.get_children()
        if self._on_unknown is not None:
            children += [self._on_unknown] + self._on_unknown.get_children()
        if self._on_error is not None:
            children += [self._on_error] + self._on_error.get_children()
        return children

    def run_step(self, msg: Message) -> None:
        """Display a message."""
        actions: List[Action] = []
        for parser in self._parsers:
            try:
                actions += parser(msg)
                if len(actions) > 0:
                    if self._on_parsed is not None:
                        new_msg = Message(
                            competition_code=msg.get_competition_code(),
                            data=actions,
                            source=msg.get_source(),
                            created_at=msg.get_created_at(),
                            updated_at=msg.get_updated_at(),
                            error_description=msg.get_error_description(),
                            error_traceback=msg.get_error_traceback(),
                        )
                        new_msg.updated()
                        self._on_parsed.run_step(new_msg)
                    if self._stop_on_first:
                        break
            except Exception as e:
                self._logger.critical(e, exc_info=True)
                if self._on_error is not None:
                    msg = Message(
                        competition_code=msg.get_competition_code(),
                        data=msg.get_data(),
                        source=msg.get_source(),
                        created_at=msg.get_created_at(),
                        updated_at=msg.get_updated_at(),
                        error_description=str(e),
                        error_traceback=str(e.__traceback__),
                    )
                    msg.updated()
                    self._on_error.run_step(msg)

        if self._on_unknown is not None:
            msg.updated()
            self._on_unknown.run_step(msg)

from datetime import datetime
import logging
from typing import Any, List, Optional

from ltspipe.data.actions import Action
from ltspipe.parsers.base import Parser
from ltspipe.messages import Message, MessageDecoder, MessageSource
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
                actions += parser(msg.data)
                if len(actions) > 0:
                    self._forward_actions(
                        actions=actions,
                        competition_code=msg.competition_code,
                        source=msg.source,
                    )
                    if self._stop_on_first:
                        break
            except Exception as e:
                self._logger.critical(e, exc_info=True)
                if self._on_error is not None:
                    msg = Message(
                        competition_code=msg.competition_code,
                        data=msg.data,
                        source=msg.source,
                        decoder=msg.decoder,
                        error_description=str(e),
                        error_traceback=str(e.__traceback__),
                    )
                    msg.updated()
                    self._on_error.run_step(msg)

        if len(actions) == 0 and self._on_unknown is not None:
            msg.updated()
            self._on_unknown.run_step(msg)

    def _forward_actions(
            self,
            actions: List[Action],
            competition_code: str,
            source: MessageSource) -> None:
        """Send actions in messages to the next step."""
        if self._on_parsed is None:
            return

        for action in actions:
            new_msg = Message(
                competition_code=competition_code,
                data=action,
                source=source,
                decoder=MessageDecoder.ACTION,
                created_at=datetime.utcnow().timestamp(),
                updated_at=datetime.utcnow().timestamp(),
            )
            self._on_parsed.run_step(new_msg)

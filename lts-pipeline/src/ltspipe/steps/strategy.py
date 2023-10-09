from datetime import datetime
from logging import Logger
from typing import Any, List, Optional

from ltspipe.data.actions import Action
from ltspipe.data.notifications import Notification
from ltspipe.messages import Message, MessageDecoder, MessageSource
from ltspipe.parsers.base import Parser
from ltspipe.steps.base import MidStep


class StrategyStep(MidStep):
    """Computes a specific strategy."""

    def __init__(
            self,
            logger: Logger,
            parser: Parser,
            on_parsed: Optional[MidStep] = None,
            on_unknown: Optional[MidStep] = None) -> None:
        """
        Construct.

        Params:
            logger (logging.Logger): Logger instance to display information.
            parser (Parser): Parser of the notification message.
            on_parsed (MidStep | None): Optionally, apply another step to the
                message when the data is parsed.
            on_unknown (MidStep | None): Optionally, apply another step to the
                message if the current parser could not detect the format.
        """
        self._logger = logger
        self._parser = parser
        self._on_parsed = on_parsed
        self._on_unknown = on_unknown

    def get_children(self) -> List[Any]:
        """Return list of children steps to this one."""
        children = []
        if self._on_parsed is not None:
            children += [self._on_parsed] + self._on_parsed.get_children()
        if self._on_unknown is not None:
            children += [self._on_unknown] + self._on_unknown.get_children()
        return children

    def run_step(self, msg: Message) -> None:
        """Run step."""
        self._logger.debug('Apply parser')
        self._apply_parser(msg, parser=self._parser)

    def _apply_parser(
            self,
            msg: Message,
            parser: Parser) -> None:
        """
        Apply a list of parser to the given message.

        Params:
            msg (Message): Message to parse.
            parser (Parser): Parser that we may apply.
        """
        if not isinstance(msg.data, Notification):
            # Skip
            return

        actions, is_parsed = parser(msg.data)

        if is_parsed:
            self._forward_actions(
                actions=actions,
                competition_code=msg.competition_code,
                source=msg.source,
            )

        if not is_parsed and self._on_unknown is not None:
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

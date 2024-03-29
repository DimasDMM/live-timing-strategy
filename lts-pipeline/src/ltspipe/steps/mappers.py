from datetime import datetime
from logging import Logger
from typing import Any, Dict, List, Optional

from ltspipe.data.actions import Action
from ltspipe.data.notifications import Notification, NotificationType
from ltspipe.parsers.base import InitialParser, Parser
from ltspipe.messages import Message, MessageDecoder, MessageSource
from ltspipe.steps.base import MidStep


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
        """Run step."""
        ntype = self._get_notification_type(msg)
        if ntype is None:
            return
        elif ntype in self._map_notification:
            self._logger.debug(f'Notification: {ntype}.')
            msg.updated()
            self._map_notification[ntype].run_step(msg)
        elif self._on_other is not None:
            msg.updated()
            self._on_other.run_step(msg)

    def _get_notification_type(
            self, msg: Message) -> Optional[NotificationType]:
        """Return the notification type if the message is a notification."""
        if isinstance(msg.data, Notification):
            return msg.data.type
        return None


class WsParsersStep(MidStep):
    """Step to parse the initial info from a websocket."""

    def __init__(
            self,
            logger: Logger,
            initial_parser: InitialParser,
            parsers: List[Parser],
            on_parsed: Optional[MidStep] = None,
            on_unknown: Optional[MidStep] = None) -> None:
        """
        Construct.

        Params:
            logger (logging.Logger): Logger instance to display information.
            initial_parser (InitialParser): Parser for initial data.
            parsers (List[Parser]): List of parsers to apply.
            on_parsed (MidStep | None): Optionally, apply another step to the
                message when the data is parsed.
            on_unknown (MidStep | None): Optionally, apply another step to the
                message if the current parser could not detect the format.
        """
        self._logger = logger
        self._initial_parser = initial_parser
        self._parsers = parsers
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
        if self._initial_parser.is_initializer_data(msg.data):
            self._logger.debug('Apply parser for initializer data')
            self._apply_parsers(
                msg, parsers=[self._initial_parser], split_lines=False)
        else:
            self._logger.debug('Apply set of parsers')
            self._apply_parsers(
                msg, parsers=self._parsers, split_lines=True)

    def _apply_parsers(
            self,
            msg: Message,
            parsers: List[Parser],
            split_lines: bool) -> None:
        """
        Apply a list of parsers to the given message.

        Params:
            msg (Message): Message to parse.
            parsers (List[Parser]): List of parsers that we may apply.
            split_lines (bool): If true, it splits the data by 'newline' and
                applies a parser to each line.
        """
        if not isinstance(msg.data, str):
            # Skip
            return

        parser_applied = False
        lines = msg.data.split('\n') if split_lines else [msg.data]
        for line in lines:
            for parser in parsers:
                actions, is_parsed = parser(line)
                if is_parsed:
                    parser_applied = True
                    self._forward_actions(
                        actions=actions,
                        competition_code=msg.competition_code,
                        source=msg.source,
                    )
                    break

        if not parser_applied and self._on_unknown is not None:
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

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
            on_unknown: Optional[MidStep] = None,
            on_error: Optional[MidStep] = None) -> None:
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
            on_error (MidStep | None): Optionally, apply another step to the
                message if the current parser had some error parsing the data.
        """
        self._logger = logger
        self._initial_parser = initial_parser
        self._parsers = parsers
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
        try:
            if self._initial_parser.is_initializer_data(msg.data):
                self._apply_parsers(
                    msg, parsers=[self._initial_parser], split_lines=False)
            else:
                self._apply_parsers(
                    msg, parsers=self._parsers, split_lines=True)
        except Exception as e:
            self._logger.critical(e, exc_info=True)
            if self._on_error is not None:
                msg = Message(
                    competition_code=msg.competition_code,
                    data=msg.data,
                    source=msg.source,
                    decoder=msg.decoder,
                    created_at=datetime.utcnow().timestamp(),
                    updated_at=datetime.utcnow().timestamp(),
                    error_description=str(e),
                    error_traceback=str(e.__traceback__),
                )
                msg.updated()
                self._on_error.run_step(msg)

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
            actions: List[Action] = []
            for parser in parsers:
                actions += parser(msg.competition_code, line)
                if len(actions) > 0:
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

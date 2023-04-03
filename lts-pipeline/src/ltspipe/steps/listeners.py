from datetime import datetime
import logging
import time
from typing import Any, List
import websocket  # type: ignore

from ltspipe.messages import Message, MessageSource
from ltspipe.steps.base import StartStep, MidStep


class WebsocketListenerStep(StartStep):
    """
    Listen incoming data from a websocket.
    """

    def __init__(
            self,
            logger: logging.Logger,
            competition_code: str,
            uri: str,
            next_step: MidStep) -> None:
        """
        Construct.

        Params:
            logger (logging.Logger): Logger instance to display information.
            competition_code (str): Verbose code to identify the competition.
            uri (str): websocket URI to get messages from.
            next_step (MidStep): The next step to apply to the message.
        """
        self._logger = logger
        self._competition_code = competition_code
        self._uri = uri
        self._next_step = next_step
        self._is_closed = False

    def get_children(self) -> List[Any]:
        """Return list of children steps to this one."""
        return [self._next_step] + self._next_step.get_children()

    def start_step(self) -> None:
        """Start listening the websocket for incoming data."""
        self._is_closed = False
        websocket.enableTrace(True)
        self._logger.debug(f'Websocket: {self._uri}')
        ws = websocket.WebSocketApp(
            self._uri,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
            on_open=self._on_open)

        while not self._is_closed:
            ws.run_forever()
            time.sleep(1)

    def _on_open(self, ws: websocket.WebSocketApp) -> None:  # noqa: U100
        """Handle open connection event."""
        self._logger.debug('Open websocket connection')

    def _on_close(self, ws: websocket.WebSocketApp) -> None:  # noqa: U100
        """Handle close connection event."""
        self._logger.debug('Close websocket connection')
        self._is_closed = True

    def _on_message(
            self,
            ws: websocket.WebSocketApp,  # noqa: U100
            data: str) -> None:
        """Handle new message event."""
        data = data.strip()
        if not data:
            self._logger.debug('Websocket data: <empty content>')
            return
        self._logger.debug(f'Websocket data: {data}')
        msg = Message(
            competition_code=self._competition_code,
            data=data,
            source=MessageSource.SOURCE_WS_LISTENER,
            created_at=datetime.utcnow().timestamp(),
            updated_at=datetime.utcnow().timestamp(),
        )
        self._next_step.run_step(msg)

    def _on_error(
            self,
            ws: websocket.WebSocketApp,  # noqa: U100
            error: str) -> None:
        """Handle an error event."""
        self._logger.error(f'Websocket error: {error}')

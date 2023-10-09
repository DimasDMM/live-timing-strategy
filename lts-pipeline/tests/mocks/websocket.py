from typing import Callable, List
import websocket

from ltspipe.exceptions import LtsError


def _default_callable(
        ws: websocket.WebSocketApp,  # noqa: U100
        *args: tuple,  # noqa: U100
        **kwargs: dict) -> None:  # noqa: U100
    """Build an empty callable for the websocket."""
    raise LtsError('Callable was not replaced.')


class MockWebSocketApp(websocket.WebSocketApp):
    """Mock of websocket.WebSocketApp."""

    def __init__(
            self,
            messages: List[str],
            on_message: Callable = _default_callable,
            on_error: Callable = _default_callable,
            on_close: Callable = _default_callable,
            on_open: Callable = _default_callable) -> None:
        """Construct."""
        self._messages = messages
        self._on_message = on_message
        self._on_error = on_error
        self._on_close = on_close
        self._on_open = on_open

    def set_on_message(self, on_message: Callable) -> None:
        """Replace callable 'on_message'."""
        self._on_message = on_message

    def set_on_error(self, on_error: Callable) -> None:
        """Replace callable 'on_error'."""
        self._on_error = on_error

    def set_on_close(self, on_close: Callable) -> None:
        """Replace callable 'on_close'."""
        self._on_close = on_close

    def set_on_open(self, on_open: Callable) -> None:
        """Replace callable 'on_open'."""
        self._on_open = on_open

    def run_forever(self, *args: tuple, **kwargs: dict) -> None:  # noqa: U100
        """Run event loop for WebSocket framework."""
        for message in self._messages:
            self._on_message(self, message)
        self._on_close(self)

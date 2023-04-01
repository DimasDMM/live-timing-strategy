from logging import Logger
from typing import Dict


class FakeLogger(Logger):
    """
    Fake logger that stores all the messages to analyse them later.

    The methods in this class should match with the ones declared
    in logging.Logger.
    """

    def __init__(self, name='fakelogger') -> None:  # noqa
        """Construct."""
        super().__init__(name=name)
        self._messages: Dict[str, list] = {
            'debug': [],
            'info': [],
            'warning': [],
            'error': [],
            'critical': [],
            'exception': [],
        }

    def get_messages(self) -> Dict[str, list]:
        """Return all received messages."""
        return self._messages

    def debug(self, msg, *args, **kwargs) -> None:  # noqa
        """Record a debug message."""
        self._messages['debug'].append(msg)

    def info(self, msg, *args, **kwargs) -> None:  # noqa
        """Record an info message."""
        self._messages['info'].append(msg)

    def warning(self, msg, *args, **kwargs) -> None:  # noqa
        """Record a warning message."""
        self._messages['warning'].append(msg)

    def error(self, msg, *args, **kwargs) -> None:  # noqa
        """Record an error message."""
        self._messages['error'].append(msg)

    def critical(self, msg, *args, **kwargs) -> None:  # noqa
        """Record a critical message."""
        self._messages['critical'].append(msg)

    def exception(self, msg, *args, **kwargs) -> None:  # noqa
        """Record an exception message."""
        self._messages['exception'].append(msg)

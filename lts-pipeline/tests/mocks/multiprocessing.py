from multiprocessing import Process as _Process
from typing import Any, Callable, Iterable, Optional


class MockProcess(_Process):
    """
    This mock replaces the parallel behaviour by a single one.

    This mock is necessary since Pytest patches do not work
    with multiprocessing.
    """

    def __init__(self, target: Callable, args: Iterable[Any]) -> None:
        """Construct."""
        self._target = target
        self._args = args

    def start(self) -> None:
        """Start process."""
        self._target(*self._args)

    def join(self) -> None:  # type: ignore
        """Mock join method."""
        return

    def kill(self) -> None:
        """Mock kill method."""
        return

    def is_alive(self) -> bool:
        """
        Mock is_alive method.

        Since this class behaves as a sequential algorithm, when this method is
        called, it should return always False.
        """
        return False

    @property
    def exitcode(self) -> Optional[int]:
        """Mock exit code."""
        return 0

    def __repr__(self) -> str:
        """Represent instance as a string."""
        txt = f'{self._target.__repr__}: {self._args}'
        return txt

    def __str__(self) -> str:
        """Represent instance as a string."""
        return self.__repr__()

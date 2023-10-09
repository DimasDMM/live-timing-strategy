import abc
from typing import Any, List, Tuple

from ltspipe.data.actions import Action


class Parser(abc.ABC):
    """Unit of data parsing."""

    @abc.abstractmethod
    def parse(
            self,
            data: Any) -> Tuple[List[Action], bool]:
        """
        Analyse and/or parse a given data.

        Params:
            data (Any): Data to parse.

        Returns:
            List[Action]: list of actions and their respective parsed data.
            bool: indicates whether the data has been parsed or not.
        """
        raise NotImplementedError

    def __call__(
            self,
            data: Any) -> Tuple[List[Action], bool]:
        """Forward to method Parser.parse()."""
        return self.parse(data)


class InitialParser(Parser, abc.ABC):
    """Unit of data parsing to initialize competition."""

    @abc.abstractmethod
    def is_initializer_data(self, data: Any) -> bool:
        """Check whether the given data is initializer or not."""
        raise NotImplementedError

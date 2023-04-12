import abc
from typing import Any, List

from ltspipe.data.actions import Action


class Parser(abc.ABC):
    """
    Unit of data parsing.
    """

    @abc.abstractmethod
    def parse(self, data: Any) -> List[Action]:
        """
        Analyse and/or parse a given data.

        Params:
            data (Any): Data to parse.

        Returns:
            List[Action]: list of actions and their respective parsed data.
        """
        raise NotImplementedError

    def __call__(self, data: Any) -> List[Action]:
        """Forward to method Parser.parse()."""
        return self.parse(data)
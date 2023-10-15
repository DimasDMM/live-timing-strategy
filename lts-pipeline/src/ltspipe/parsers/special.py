import re
from typing import Any, List, Tuple

from ltspipe.data.actions import Action
from ltspipe.data.competitions import CompetitionInfo
from ltspipe.data.enum import ParserSettings
from ltspipe.parsers.base import Parser
from ltspipe.utils import is_column_parser_setting


class IgnoreParser(Parser):
    """
    Ignore certain messages.
    """

    def __init__(self, info: CompetitionInfo) -> None:
        """Construct."""
        self._info = info

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
        if not isinstance(data, str):
            return [], False

        if self._is_ignore_type(data):
            return [], True

        return [], False

    def _is_ignore_type(self, data: str) -> bool:
        """Parse driver name."""
        data = data.strip()
        matches = re.match(r'^(.+?)(c\d+)\|.+$', data)
        if matches is None:
            return False

        column_id = matches[2]
        return (
            is_column_parser_setting(
                self._info,
                column_id,
                ParserSettings.IGNORE_GRP,
                raise_exception=False)
            or is_column_parser_setting(
                self._info,
                column_id,
                ParserSettings.IGNORE_STA,
                raise_exception=False)
        )

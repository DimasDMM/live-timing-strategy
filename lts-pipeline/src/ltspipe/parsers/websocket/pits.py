import re
from typing import Any, List, Tuple

from ltspipe.data.actions import Action, ActionType
from ltspipe.data.competitions import (
    AddPitIn,
    AddPitOut,
    CompetitionInfo,
)
from ltspipe.exceptions import LtsError
from ltspipe.parsers.base import Parser
from ltspipe.parsers.websocket.base import _find_team_by_code


class PitInParser(Parser):
    """
    Parse that a participant has entered the pit.

    Sample messages:
    > r5625|*in|0
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

        data = data.strip()
        matches = re.match(r'^(.+?)\|\*in\|.*$', data)
        if matches is None:
            return [], False

        participant_code = matches[1]

        team = _find_team_by_code(
            info=self._info,
            team_code=participant_code)

        if team is None:
            raise LtsError(f'Unknown team with code={participant_code}')

        action = Action(
            type=ActionType.ADD_PIT_IN,
            data=AddPitIn(
                competition_code=self._info.competition_code,
                team_id=team.id,
            ),
        )
        return [action], True


class PitOutParser(Parser):
    """
    Parse that a participant has left the pit.

    Sample messages:
    > r5625|*out|0
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

        data = data.strip()
        matches = re.match(r'^(.+?)\|\*out\|.*$', data)
        if matches is None:
            return [], False

        participant_code = matches[1]

        team = _find_team_by_code(
            info=self._info,
            team_code=participant_code)

        if team is None:
            raise LtsError(f'Unknown team with code={participant_code}')

        action = Action(
            type=ActionType.ADD_PIT_OUT,
            data=AddPitOut(
                competition_code=self._info.competition_code,
                team_id=team.id,
            ),
        )
        return [action], True

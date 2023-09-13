import re
from typing import Any, Dict, List, Tuple

from ltspipe.data.actions import Action, ActionType
from ltspipe.data.competitions import (
    AddPitIn,
    AddPitOut,
    CompetitionInfo,
)
from ltspipe.parsers.base import Parser
from ltspipe.parsers.websocket.base import _find_team_by_code


class PitInParser(Parser):
    """
    Parse that a participant has entered the pit.

    Sample messages:
    > r5625|*in|0
    """

    def __init__(self, competitions: Dict[str, CompetitionInfo]) -> None:
        """Construct."""
        self._competitions = competitions

    def parse(
            self,
            competition_code: str,
            data: Any) -> Tuple[List[Action], bool]:
        """
        Analyse and/or parse a given data.

        Params:
            competition_code (str): Code of the competition.
            data (Any): Data to parse.

        Returns:
            List[Action]: list of actions and their respective parsed data.
            bool: indicates whether the data has been parsed or not.
        """
        if competition_code not in self._competitions:
            raise Exception(f'Unknown competition with code={competition_code}')
        elif not isinstance(data, str):
            return [], False

        data = data.strip()
        matches = re.match(r'^(.+?)\|\*in\|.*$', data)
        if matches is None:
            return [], False

        participant_code = matches[1]

        team = _find_team_by_code(
            self._competitions,
            competition_code,
            team_code=participant_code)

        if team is None:
            raise Exception(f'Unknown team with code={participant_code}')

        action = Action(
            type=ActionType.ADD_PIT_IN,
            data=AddPitIn(
                competition_code=competition_code,
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

    def __init__(self, competitions: Dict[str, CompetitionInfo]) -> None:
        """Construct."""
        self._competitions = competitions

    def parse(
            self,
            competition_code: str,
            data: Any) -> Tuple[List[Action], bool]:
        """
        Analyse and/or parse a given data.

        Params:
            competition_code (str): Code of the competition.
            data (Any): Data to parse.

        Returns:
            List[Action]: list of actions and their respective parsed data.
            bool: indicates whether the data has been parsed or not.
        """
        if competition_code not in self._competitions:
            raise Exception(f'Unknown competition with code={competition_code}')
        elif not isinstance(data, str):
            return [], False

        data = data.strip()
        matches = re.match(r'^(.+?)\|\*out\|.*$', data)
        if matches is None:
            return [], False

        participant_code = matches[1]

        team = _find_team_by_code(
            self._competitions,
            competition_code,
            team_code=participant_code)

        if team is None:
            raise Exception(f'Unknown team with code={participant_code}')

        action = Action(
            type=ActionType.ADD_PIT_OUT,
            data=AddPitOut(
                competition_code=competition_code,
                team_id=team.id,
            ),
        )
        return [action], True

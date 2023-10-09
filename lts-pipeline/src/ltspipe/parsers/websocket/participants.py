import re
from typing import Any, List, Optional, Tuple

from ltspipe.data.actions import Action, ActionType
from ltspipe.data.competitions import (
    CompetitionInfo,
    Team,
    UpdateDriver,
    UpdateTeam,
)
from ltspipe.data.enum import ParserSettings
from ltspipe.exceptions import LtsError
from ltspipe.parsers.base import Parser
from ltspipe.parsers.websocket.base import (
    _find_driver_by_name,
    _find_team_by_code,
    _is_column_parser_setting,
)


class DriverNameParser(Parser):
    """
    Parse the name of a driver and, optionally, total driving time.

    Sample messages:
    > r5625c5|drteam|NOMBRE
    > r5625c5|drteam|NOMBRE [1:08]

    Note: If the total driving time is provided within the name, it is ignored
    by this parser.
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

        parsed_data = self._parse_driver_name(data)
        if parsed_data is None:
            return [], False

        action = Action(
            type=ActionType.UPDATE_DRIVER,
            data=parsed_data,
        )
        return [action], True

    def _parse_driver_name(
            self,
            data: str) -> Optional[UpdateDriver]:
        """Parse driver name."""
        data = data.strip()
        # TODO: Update stint time too
        matches = re.match(
            r'^(.+?)(c\d+)\|drteam\|(.+?)( \[\d+:\d+\])?$', data)
        if matches is None:
            return None

        column_id = matches[2]
        if not _is_column_parser_setting(
                self._info,
                column_id,
                ParserSettings.TIMING_NAME):
            return None

        participant_code = matches[1]
        driver_name = matches[3]

        old_driver = _find_driver_by_name(self._info, driver_name)
        team: Optional[Team] = _find_team_by_code(
            info=self._info,
            team_code=participant_code)
        if team is None:
            raise LtsError(f'Unknown team with code={participant_code}')

        updated_driver = UpdateDriver(
            id=(None if old_driver is None else old_driver.id),
            competition_code=self._info.competition_code,
            participant_code=participant_code,
            name=driver_name,
            number=team.number,
            team_id=team.id,
        )
        return updated_driver


class TeamNameParser(Parser):
    """Parse the name of a team."""

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

        parsed_data = self._parse_team_name(data)
        if parsed_data is None:
            return [], False

        action = Action(
            type=ActionType.UPDATE_TEAM,
            data=parsed_data,
        )
        return [action], True

    def _parse_team_name(
            self,
            data: str) -> Optional[UpdateTeam]:
        """Parse team name."""
        data = data.strip()
        matches = re.match(r'^(.+?)(c\d+)\|dr\|(.+)$', data)
        if matches is None:
            return None

        column_id = matches[2]
        if not _is_column_parser_setting(
                self._info,
                column_id,
                ParserSettings.TIMING_NAME):
            return None

        participant_code = matches[1]
        old_team: Optional[Team] = _find_team_by_code(
            self._info,
            team_code=participant_code)

        if old_team is None:
            raise LtsError(f'Unknown team with code={participant_code}')

        updated_team = UpdateTeam(
            id=old_team.id,
            competition_code=self._info.competition_code,
            participant_code=participant_code,
            name=matches[3],
            number=old_team.number,
        )
        return updated_team

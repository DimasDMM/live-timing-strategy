import re
from typing import Any, Dict, List, Optional

from ltspipe.data.actions import Action, ActionType
from ltspipe.data.competitions import (
    CompetitionInfo,
    Driver,
    Team,
    UpdateDriver,
    UpdateTeam,
)
from ltspipe.data.enum import ParserSettings
from ltspipe.parsers.base import Parser


def _find_driver(
        competitions: Dict[str, CompetitionInfo],
        competition_code: str,
        driver_name: str) -> Optional[Driver]:
    """Find a driver in the competition info."""
    info = competitions[competition_code]
    for d in info.drivers:
        if d.name == driver_name:
            return d
    return None


def _find_team(
        competitions: Dict[str, CompetitionInfo],
        competition_code: str,
        team_code: str) -> Team:
    """Find a team in the competition info."""
    info = competitions[competition_code]
    for t in info.teams:
        if t.participant_code == team_code:
            return t
    raise Exception(f'Unknown team with code={team_code}')


def _validate_column_name(
        competitions: Dict[str, CompetitionInfo],
        competition_code: str,
        column_id: str) -> None:
    """Validate that the column correspond to the participant name."""
    info = competitions[competition_code]
    if ParserSettings.TIMING_NAME in info.parser_settings:
        name_id = info.parser_settings[ParserSettings.TIMING_NAME]
        if name_id != column_id:
            raise Exception(
                f'The expected column for the name is "{name_id}", '
                f'but it was given in "{column_id}"')
        else:
            return

    raise Exception('Column for name not found')


class DriverNameParser(Parser):
    """
    Parse the name of a driver and, optionally, total driving time.

    Sample messages:
    > r5625c5|drteam|NOMBRE
    > r5625c5|drteam|NOMBRE [1:08]

    Note: If the total driving time is provided within the name, it is ignored
    by this parser.
    """

    def __init__(self, competitions: Dict[str, CompetitionInfo]) -> None:
        """Construct."""
        self._competitions = competitions

    def parse(self, competition_code: str, data: Any) -> List[Action]:
        """
        Analyse and/or parse a given data.

        Params:
            competition_code (str): Code of the competition.
            data (Any): Data to parse.

        Returns:
            List[Action]: list of actions and their respective parsed data.
        """
        if competition_code not in self._competitions:
            raise Exception(f'Unknown competition with code={competition_code}')
        elif not isinstance(data, str):
            return []

        parsed_data = self._parse_driver_name(competition_code, data)
        if parsed_data is None:
            return []

        action = Action(
            type=ActionType.UPDATE_DRIVER,
            data=parsed_data,
        )
        return [action]

    def _parse_driver_name(
            self,
            competition_code: str,
            data: str) -> Optional[UpdateDriver]:
        """Parse driver name."""
        data = data.strip()
        matches = re.match(
            r'^(.+?)(c\d+)\|drteam\|(.+?)( \[\d+:\d+\])?$', data)
        if matches is None:
            return None

        column_id = matches[2]
        _validate_column_name(self._competitions, competition_code, column_id)

        driver_code = matches[1]
        driver_name = matches[3]

        old_driver = _find_driver(
            self._competitions,
            competition_code,
            driver_name)
        team = _find_team(
            self._competitions,
            competition_code,
            team_code=driver_code)

        updated_driver = UpdateDriver(
            id=(None if old_driver is None else old_driver.id),
            competition_code=competition_code,
            participant_code=driver_code,
            name=driver_name,
            number=team.number,
            team_id=team.id,
        )
        return updated_driver


class TeamNameParser(Parser):
    """Parse the name of a team."""

    def __init__(self, competitions: Dict[str, CompetitionInfo]) -> None:
        """Construct."""
        self._competitions = competitions

    def parse(self, competition_code: str, data: Any) -> List[Action]:
        """
        Analyse and/or parse a given data.

        Params:
            competition_code (str): Code of the competition.
            data (Any): Data to parse.

        Returns:
            List[Action]: list of actions and their respective parsed data.
        """
        if competition_code not in self._competitions:
            raise Exception(f'Unknown competition with code={competition_code}')
        elif not isinstance(data, str):
            return []

        parsed_data = self._parse_team_name(competition_code, data)
        if parsed_data is None:
            return []

        action = Action(
            type=ActionType.UPDATE_TEAM,
            data=parsed_data,
        )
        return [action]

    def _parse_team_name(
            self,
            competition_code: str,
            data: str) -> Optional[UpdateTeam]:
        """Parse team name."""
        data = data.strip()
        matches = re.match(r'^(.+?)(c\d+)\|dr\|(.+)$', data)
        if matches is None:
            return None

        column_id = matches[2]
        _validate_column_name(self._competitions, competition_code, column_id)

        team_code = matches[1]
        old_team = _find_team(self._competitions, competition_code, team_code)

        updated_team = UpdateTeam(
            id=old_team.id,
            competition_code=competition_code,
            participant_code=team_code,
            name=matches[3],
            number=old_team.number,
        )
        return updated_team

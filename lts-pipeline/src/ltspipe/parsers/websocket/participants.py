import re
from typing import Any, List, Optional, Tuple

from ltspipe.data.actions import Action, ActionType
from ltspipe.data.competitions import (
    CompetitionInfo,
    Team,
    UpdateDriver,
    UpdateDriverPartialDrivingTime,
    UpdateTeam,
)
from ltspipe.data.enum import ParserSettings
from ltspipe.exceptions import LtsError
from ltspipe.parsers.base import Parser
from ltspipe.utils import (
    find_driver_by_name,
    find_team_by_code,
    is_column_parser_setting,
    time_to_millis,
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
        if not is_column_parser_setting(
                self._info,
                column_id,
                ParserSettings.TIMING_NAME,
                raise_exception=False):
            return None

        participant_code = matches[1]
        driver_name = matches[3]

        old_driver = find_driver_by_name(
            info=self._info,
            participant_code=participant_code,
            driver_name=driver_name)
        team: Optional[Team] = find_team_by_code(
            info=self._info,
            participant_code=participant_code)
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


class DriverPartialDrivingTimeParser(Parser):
    """
    Parse the time a driver has been driving in the stint.

    Sample messages:
    > r5625c11|in|1:05
    > r5625c11|in|0:10

    Note: Do not confuse this message with the 'pit time'.
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

        parsed_data, is_parsed = self._parse_timing_pit_time(data)
        if parsed_data is None:
            return [], is_parsed

        action = Action(
            type=ActionType.UPDATE_DRIVER_PARTIAL_DRIVING_TIME,
            data=parsed_data,
        )
        return [action], True

    def _parse_timing_pit_time(
            self,
            data: str) -> Tuple[Optional[UpdateDriverPartialDrivingTime], bool]:
        """Parse driver name."""
        data = data.strip()
        matches = re.match(r'^(.+?)(c\d+)\|in\|((?:\d+:)?\d+)$', data)
        if matches is None:
            return None, False

        # Note: The driving time is in the same column like the pit time
        column_id = matches[2]
        if not is_column_parser_setting(
                self._info,
                column_id,
                ParserSettings.TIMING_PIT_TIME,
                raise_exception=False):
            return None, False

        participant_code = matches[1]
        raw_pit_time = matches[3]

        driving_time: int = time_to_millis(  # type: ignore
            raw_pit_time,
            default=0)

        # The driver must be already initialized
        timing = self._info.timing.get(participant_code, None)
        if timing is None:
            raise LtsError(
                f'Unknown participant timing with code={participant_code}')

        if timing.driver_id is None:
            return None, True

        updated_timing = UpdateDriverPartialDrivingTime(
            id=timing.driver_id,
            competition_code=self._info.competition_code,
            partial_driving_time=driving_time,
            auto_compute_total=False,
        )
        return updated_timing, True


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
        if not is_column_parser_setting(
                self._info,
                column_id,
                ParserSettings.TIMING_NAME,
                raise_exception=False):
            return None

        participant_code = matches[1]
        old_team: Optional[Team] = find_team_by_code(
            self._info,
            participant_code=participant_code)

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

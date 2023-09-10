import re
from typing import Any, Dict, List, Optional

from ltspipe.data.actions import Action, ActionType
from ltspipe.data.competitions import (
    CompetitionInfo,
    UpdateTimingLap,
    UpdateTimingLastTime,
    UpdateTimingPosition,
)
from ltspipe.data.enum import ParserSettings
from ltspipe.parsers.base import Parser
from ltspipe.parsers.websocket import _find_team_by_code


def _validate_column_parser_setting(
        competitions: Dict[str, CompetitionInfo],
        competition_code: str,
        column_id: str,
        parser_setting: ParserSettings) -> None:
    """Validate that the column correspond to the expected data."""
    info = competitions[competition_code]
    if parser_setting in info.parser_settings:
        name_id = info.parser_settings[parser_setting]
        if name_id != column_id:
            raise Exception(
                f'The expected column for the {parser_setting} is "{name_id}", '
                f'but it was given in "{column_id}"')
        else:
            return

    raise Exception(f'Column for {parser_setting} not found')


class TimingLapParser(Parser):
    """
    Parse the lap in the timing of a team.

    Sample messages:
    > r5625c6|in|143
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

        parsed_data = self._parse_timing_lap(competition_code, data)
        if parsed_data is None:
            return []

        action = Action(
            type=ActionType.UPDATE_TIMING_LAP,
            data=parsed_data,
        )
        return [action]

    def _parse_timing_lap(
            self,
            competition_code: str,
            data: str) -> Optional[UpdateTimingLap]:
        """Parse driver name."""
        data = data.strip()
        matches = re.match(
            r'^(.+?)(c\d+)\|in\|(\d+)$', data)
        if matches is None:
            return None

        column_id = matches[2]
        _validate_column_parser_setting(
            self._competitions,
            competition_code,
            column_id,
            ParserSettings.TIMING_LAP)

        participant_code = matches[1]
        timing_lap = int(matches[3])

        # The team must be already initialized
        team = _find_team_by_code(
            self._competitions,
            competition_code,
            team_code=participant_code)
        if team is None:
            raise Exception(f'Unknown team with code={participant_code}')

        updated_timing = UpdateTimingLap(
            competition_code=competition_code,
            team_id=team.id,
            lap=timing_lap,
        )
        return updated_timing


class TimingLastTimeParser(Parser):
    """
    Parse the last time in the timing of a team.

    Sample messages:
    > r5625c7|tn|1:05.739
    """

    # The following regex matches the following samples:
    # > '2:12.283'
    # > '00:20:00'
    # > '54.'
    REGEX_TIME = r'^\+?(?:(?:(\d+):)?(\d+):)?(\d+)(?:\.(\d+)?)?$'

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

        parsed_data = self._parse_timing_last_time(competition_code, data)
        if parsed_data is None:
            return []

        action = Action(
            type=ActionType.UPDATE_TIMING_LAST_TIME,
            data=parsed_data,
        )
        return [action]

    def _parse_timing_last_time(
            self,
            competition_code: str,
            data: str) -> Optional[UpdateTimingLastTime]:
        """Parse driver name."""
        data = data.strip()
        matches = re.match(
            r'^(.+?)(c\d+)\|tn\|(.+)$', data)
        if matches is None:
            return None

        column_id = matches[2]
        _validate_column_parser_setting(
            self._competitions,
            competition_code,
            column_id,
            ParserSettings.TIMING_LAST_TIME)

        participant_code = matches[1]
        raw_timing_last_time = matches[3]

        # The team must be already initialized
        team = _find_team_by_code(
            self._competitions,
            competition_code,
            team_code=participant_code)
        if team is None:
            raise Exception(f'Unknown team with code={participant_code}')

        timing_last_time = self._time_to_millis(raw_timing_last_time, default=0)
        updated_timing = UpdateTimingLastTime(
            competition_code=competition_code,
            team_id=team.id,
            last_time=timing_last_time,
            auto_best_time=True,
        )
        return updated_timing

    def _time_to_millis(
            self,
            lap_time: Optional[str],
            default: Optional[int] = None) -> Optional[int]:
        """Transform a lap time into milliseconds."""
        if lap_time is None:
            return default
        lap_time = lap_time.strip()
        match = re.search(self.REGEX_TIME, lap_time)
        if match is None:
            return default
        else:
            parts = [int(p) if p else 0 for p in match.groups()]
            return (parts[0] * 3600000
                + parts[1] * 60000
                + parts[2] * 1000
                + parts[3])


class TimingPositionParser(Parser):
    """
    Parse the position in the timing of a team.

    Sample messages:
    > r5625c3||6
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

        parsed_data = self._parse_timing_position(competition_code, data)
        if parsed_data is None:
            return []

        action = Action(
            type=ActionType.UPDATE_TIMING_POSITION,
            data=parsed_data,
        )
        return [action]

    def _parse_timing_position(
            self,
            competition_code: str,
            data: str) -> Optional[UpdateTimingPosition]:
        """Parse driver name."""
        data = data.strip()
        matches = re.match(
            r'^(.+?)(c\d+)\|\|(\d+)$', data)
        if matches is None:
            return None

        column_id = matches[2]
        _validate_column_parser_setting(
            self._competitions,
            competition_code,
            column_id,
            ParserSettings.TIMING_POSITION)

        participant_code = matches[1]
        timing_position = int(matches[3])

        # The team must be already initialized
        team = _find_team_by_code(
            self._competitions,
            competition_code,
            team_code=participant_code)
        if team is None:
            raise Exception(f'Unknown team with code={participant_code}')

        updated_timing = UpdateTimingPosition(
            competition_code=competition_code,
            team_id=team.id,
            position=timing_position,
            auto_other_positions=True,
        )
        return updated_timing

import re
from typing import Any, Dict, List, Optional, Tuple

from ltspipe.data.actions import Action, ActionType
from ltspipe.data.competitions import (
    CompetitionInfo,
    UpdateTimingBestTime,
    UpdateTimingLap,
    UpdateTimingLastTime,
    UpdateTimingNumberPits,
    UpdateTimingPitTime,
    UpdateTimingPosition,
)
from ltspipe.data.enum import ParserSettings
from ltspipe.parsers.base import Parser
from ltspipe.parsers.websocket.base import (
    _find_team_by_code,
    _is_column_parser_setting,
    _time_to_millis,
)


class TimingBestTimeParser(Parser):
    """
    Parse the best time in the timing of a team.

    Sample messages:
    > r5625c8|tb|1:05.739
    > r5625c8|tn|1:05.739
    > r5625c8|ib|1:05.739
    > r5625c8|in|1:05.739
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

        parsed_data = self._parse_timing_best_time(competition_code, data)
        if parsed_data is None:
            return [], False

        action = Action(
            type=ActionType.UPDATE_TIMING_BEST_TIME,
            data=parsed_data,
        )
        return [action], True

    def _parse_timing_best_time(
            self,
            competition_code: str,
            data: str) -> Optional[UpdateTimingBestTime]:
        """Parse driver name."""
        data = data.strip()
        matches = re.match(
            r'^(.+?)(c\d+)\|(?:tb|tn|ib|in)\|(.+)$', data)
        if matches is None:
            return None

        column_id = matches[2]
        if not _is_column_parser_setting(
                self._competitions,
                competition_code,
                column_id,
                ParserSettings.TIMING_BEST_TIME):
            return None

        participant_code = matches[1]
        raw_timing_best_time = matches[3]

        # The team must be already initialized
        team = _find_team_by_code(
            self._competitions,
            competition_code,
            team_code=participant_code)
        if team is None:
            raise Exception(f'Unknown team with code={participant_code}')

        timing_best_time = _time_to_millis(raw_timing_best_time, default=0)
        updated_timing = UpdateTimingBestTime(
            competition_code=competition_code,
            team_id=team.id,
            best_time=timing_best_time,
        )
        return updated_timing


class TimingLapParser(Parser):
    """
    Parse the lap in the timing of a team.

    Sample messages:
    > r5625c6|in|143
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

        parsed_data = self._parse_timing_lap(competition_code, data)
        if parsed_data is None:
            return [], False

        action = Action(
            type=ActionType.UPDATE_TIMING_LAP,
            data=parsed_data,
        )
        return [action], True

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
        if not _is_column_parser_setting(
                self._competitions,
                competition_code,
                column_id,
                ParserSettings.TIMING_LAP,
                raise_exception=False):
            return None

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
    > r5625c7|tb|1:05.739
    > r5625c8|tn|1:05.739
    > r5625c8|ib|1:05.739
    > r5625c8|in|1:05.739
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

        parsed_data = self._parse_timing_last_time(competition_code, data)
        if parsed_data is None:
            return [], False

        action = Action(
            type=ActionType.UPDATE_TIMING_LAST_TIME,
            data=parsed_data,
        )
        return [action], True

    def _parse_timing_last_time(
            self,
            competition_code: str,
            data: str) -> Optional[UpdateTimingLastTime]:
        """Parse driver name."""
        data = data.strip()
        matches = re.match(
            r'^(.+?)(c\d+)\|(?:tb|tn|ib|in)\|(.+)$', data)
        if matches is None:
            return None

        column_id = matches[2]
        if not _is_column_parser_setting(
                self._competitions,
                competition_code,
                column_id,
                ParserSettings.TIMING_LAST_TIME):
            return None

        participant_code = matches[1]
        raw_timing_last_time = matches[3]

        # The team must be already initialized
        team = _find_team_by_code(
            self._competitions,
            competition_code,
            team_code=participant_code)
        if team is None:
            raise Exception(f'Unknown team with code={participant_code}')

        timing_last_time = _time_to_millis(raw_timing_last_time, default=0)
        updated_timing = UpdateTimingLastTime(
            competition_code=competition_code,
            team_id=team.id,
            last_time=timing_last_time,
            auto_best_time=True,
        )
        return updated_timing


class TimingPitTimeParser(Parser):
    """
    Parse the time a participant is in a pit.

    Sample messages:
    > r5625c11|to|10.
    > r5625c11|to|1:10.
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

        parsed_data = self._parse_timing_pit_time(competition_code, data)
        if parsed_data is None:
            return [], False

        action = Action(
            type=ActionType.UPDATE_TIMING_PIT_TIME,
            data=parsed_data,
        )
        return [action], True

    def _parse_timing_pit_time(
            self,
            competition_code: str,
            data: str) -> Optional[UpdateTimingPitTime]:
        """Parse driver name."""
        data = data.strip()
        matches = re.match(r'^(.+?)(c\d+)\|to\|((?:\d+:)?\d+\.?)$', data)
        if matches is None:
            return None

        column_id = matches[2]
        if not _is_column_parser_setting(
                self._competitions,
                competition_code,
                column_id,
                ParserSettings.TIMING_PIT_TIME):
            return None

        participant_code = matches[1]
        raw_pit_time = matches[3]

        timing_pit_time = _time_to_millis(raw_pit_time, default=0)

        # The team must be already initialized
        team = _find_team_by_code(
            self._competitions,
            competition_code,
            team_code=participant_code)
        if team is None:
            raise Exception(f'Unknown team with code={participant_code}')

        updated_timing = UpdateTimingPitTime(
            competition_code=competition_code,
            team_id=team.id,
            pit_time=timing_pit_time,
        )
        return updated_timing


class TimingPositionParser(Parser):
    """
    Parse the position in the timing of a team.

    Sample messages:
    > r5625c3||6
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

        parsed_data = self._parse_timing_position(competition_code, data)
        if parsed_data is None:
            return [], False

        action = Action(
            type=ActionType.UPDATE_TIMING_POSITION,
            data=parsed_data,
        )
        return [action], True

    def _parse_timing_position(
            self,
            competition_code: str,
            data: str) -> Optional[UpdateTimingPosition]:
        """Parse driver name."""
        data = data.strip()
        matches = re.match(r'^(.+?)(c\d+)\|\|(\d+)$', data)
        if matches is None:
            return None

        column_id = matches[2]
        if not _is_column_parser_setting(
                self._competitions,
                competition_code,
                column_id,
                ParserSettings.TIMING_POSITION):
            return None

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


class TimingNumberPitsParser(Parser):
    """
    Parse the number of pits in the timing of a team.

    Sample messages:
    > r5625c12|in|2
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

        parsed_data = self._parse_timing_number_pits(competition_code, data)
        if parsed_data is None:
            return [], False

        action = Action(
            type=ActionType.UPDATE_TIMING_NUMBER_PITS,
            data=parsed_data,
        )
        return [action], True

    def _parse_timing_number_pits(
            self,
            competition_code: str,
            data: str) -> Optional[UpdateTimingNumberPits]:
        """Parse driver name."""
        data = data.strip()
        matches = re.match(
            r'^(.+?)(c\d+)\|in\|(\d+)$', data)
        if matches is None:
            return None

        column_id = matches[2]
        if not _is_column_parser_setting(
                self._competitions,
                competition_code,
                column_id,
                ParserSettings.TIMING_NUMBER_PITS):
            return None

        participant_code = matches[1]
        number_pits = int(matches[3])

        # The team must be already initialized
        team = _find_team_by_code(
            self._competitions,
            competition_code,
            team_code=participant_code)
        if team is None:
            raise Exception(f'Unknown team with code={participant_code}')

        updated_timing = UpdateTimingNumberPits(
            competition_code=competition_code,
            team_id=team.id,
            number_pits=number_pits,
        )
        return updated_timing

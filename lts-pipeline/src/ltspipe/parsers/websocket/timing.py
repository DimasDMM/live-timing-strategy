import re
from typing import Any, List, Optional, Tuple

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
from ltspipe.exceptions import LtsError
from ltspipe.parsers.base import Parser
from ltspipe.utils import (
    find_team_by_code,
    is_column_parser_setting,
    time_to_millis,
)


class TimingBestTimeParser(Parser):
    """
    Parse the best time in the timing of a team.

    Sample messages:
    > r5625c8|tb|1:05.739
    > r5625c8|tn|1:05.739
    > r5625c8|ib|1:05.739
    > r5625c8|in|1:05.739
    > r5625c8|ti|1:05.739
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

        parsed_data = self._parse_timing_best_time(data)
        if parsed_data is None:
            return [], False

        action = Action(
            type=ActionType.UPDATE_TIMING_BEST_TIME,
            data=parsed_data,
        )
        return [action], True

    def _parse_timing_best_time(
            self,
            data: str) -> Optional[UpdateTimingBestTime]:
        """Parse driver name."""
        data = data.strip()
        matches = re.match(
            r'^(.+?)(c\d+)\|(?:tb|tn|ib|in|ti)\|(.+)$', data)
        if matches is None:
            return None

        column_id = matches[2]
        if not is_column_parser_setting(
                self._info,
                column_id,
                ParserSettings.TIMING_BEST_TIME,
                raise_exception=False):
            return None

        participant_code = matches[1]
        raw_timing_best_time = matches[3]

        # The team must be already initialized
        team = find_team_by_code(
            info=self._info,
            participant_code=participant_code)
        if team is None:
            raise LtsError(f'Unknown team with code={participant_code}')

        timing_best_time: int = time_to_millis(  # type: ignore
            raw_timing_best_time,
            default=0)
        updated_timing = UpdateTimingBestTime(
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

        parsed_data = self._parse_timing_lap(data)
        if parsed_data is None:
            return [], False

        action = Action(
            type=ActionType.UPDATE_TIMING_LAP,
            data=parsed_data,
        )
        return [action], True

    def _parse_timing_lap(
            self,
            data: str) -> Optional[UpdateTimingLap]:
        """Parse driver name."""
        data = data.strip()
        matches = re.match(
            r'^(.+?)(c\d+)\|in\|(\d+)$', data)
        if matches is None:
            return None

        column_id = matches[2]
        if not is_column_parser_setting(
                self._info,
                column_id,
                ParserSettings.TIMING_LAP,
                raise_exception=False):
            return None

        participant_code = matches[1]
        timing_lap = int(matches[3])

        # The team must be already initialized
        team = find_team_by_code(
            info=self._info,
            participant_code=participant_code)
        if team is None:
            raise LtsError(f'Unknown team with code={participant_code}')

        updated_timing = UpdateTimingLap(
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
    > r5625c8|ti|1:05.739
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

        parsed_data = self._parse_timing_last_time(data)
        if parsed_data is None:
            return [], False

        action = Action(
            type=ActionType.UPDATE_TIMING_LAST_TIME,
            data=parsed_data,
        )
        return [action], True

    def _parse_timing_last_time(
            self,
            data: str) -> Optional[UpdateTimingLastTime]:
        """Parse driver name."""
        data = data.strip()
        matches = re.match(
            r'^(.+?)(c\d+)\|(?:tb|tn|ib|in|ti)\|(.+)$', data)
        if matches is None:
            return None

        column_id = matches[2]
        if not is_column_parser_setting(
                self._info,
                column_id,
                ParserSettings.TIMING_LAST_TIME,
                raise_exception=False):
            return None

        participant_code = matches[1]
        raw_timing_last_time = matches[3]

        # The team must be already initialized
        team = find_team_by_code(
            info=self._info,
            participant_code=participant_code)
        if team is None:
            raise LtsError(f'Unknown team with code={participant_code}')

        timing_last_time: int = time_to_millis(  # type: ignore
            raw_timing_last_time,
            default=0)
        updated_timing = UpdateTimingLastTime(
            team_id=team.id,
            last_time=timing_last_time,
            auto_best_time=True,
        )
        return updated_timing


class TimingNumberPitsParser(Parser):
    """
    Parse the number of pits in the timing of a team.

    Sample messages:
    > r5625c12|in|2
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

        parsed_data = self._parse_timing_number_pits(data)
        if parsed_data is None:
            return [], False

        action = Action(
            type=ActionType.UPDATE_TIMING_NUMBER_PITS,
            data=parsed_data,
        )
        return [action], True

    def _parse_timing_number_pits(
            self,
            data: str) -> Optional[UpdateTimingNumberPits]:
        """Parse driver name."""
        data = data.strip()
        matches = re.match(
            r'^(.+?)(c\d+)\|in\|(\d+)$', data)
        if matches is None:
            return None

        column_id = matches[2]
        if not is_column_parser_setting(
                self._info,
                column_id,
                ParserSettings.TIMING_NUMBER_PITS,
                raise_exception=False):
            return None

        participant_code = matches[1]
        number_pits = int(matches[3])

        # The team must be already initialized
        team = find_team_by_code(
            info=self._info,
            participant_code=participant_code)
        if team is None:
            raise LtsError(f'Unknown team with code={participant_code}')

        updated_timing = UpdateTimingNumberPits(
            team_id=team.id,
            number_pits=number_pits,
        )
        return updated_timing


class TimingPitTimeParser(Parser):
    """
    Parse the time a participant is in a pit.

    Sample messages:
    > r5625c11|to|10.
    > r5625c11|to|1:10.

    Note: Do not confuse this message with the 'driver stint time'.
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

        parsed_data = self._parse_timing_pit_time(data)
        if parsed_data is None:
            return [], False

        action = Action(
            type=ActionType.UPDATE_TIMING_PIT_TIME,
            data=parsed_data,
        )
        return [action], True

    def _parse_timing_pit_time(
            self,
            data: str) -> Optional[UpdateTimingPitTime]:
        """Parse driver name."""
        data = data.strip()
        matches = re.match(r'^(.+?)(c\d+)\|to\|((?:\d+:)?\d+\.?)$', data)
        if matches is None:
            return None

        column_id = matches[2]
        if not is_column_parser_setting(
                self._info,
                column_id,
                ParserSettings.TIMING_PIT_TIME,
                raise_exception=False):
            return None

        participant_code = matches[1]
        raw_pit_time = matches[3]

        timing_pit_time: int = time_to_millis(  # type: ignore
            raw_pit_time,
            default=0)

        # The team must be already initialized
        team = find_team_by_code(
            info=self._info,
            participant_code=participant_code)
        if team is None:
            raise LtsError(f'Unknown team with code={participant_code}')

        updated_timing = UpdateTimingPitTime(
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

        parsed_data = self._parse_timing_position(data)
        if parsed_data is None:
            return [], False

        action = Action(
            type=ActionType.UPDATE_TIMING_POSITION,
            data=parsed_data,
        )
        return [action], True

    def _parse_timing_position(
            self,
            data: str) -> Optional[UpdateTimingPosition]:
        """Parse driver name."""
        data = data.strip()
        matches = re.match(r'^(.+?)(c\d+)\|\|(\d+)$', data)
        if matches is None:
            return None

        column_id = matches[2]
        if not is_column_parser_setting(
                self._info,
                column_id,
                ParserSettings.TIMING_POSITION,
                raise_exception=False):
            return None

        participant_code = matches[1]
        timing_position = int(matches[3])

        # The team must be already initialized
        team = find_team_by_code(
            info=self._info,
            participant_code=participant_code)
        if team is None:
            raise LtsError(f'Unknown team with code={participant_code}')

        updated_timing = UpdateTimingPosition(
            team_id=team.id,
            position=timing_position,
            auto_other_positions=True,
        )
        return updated_timing

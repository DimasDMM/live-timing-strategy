import re
from typing import Any, Dict, List, Optional, Tuple

from ltspipe.data.actions import Action, ActionType
from ltspipe.data.competitions import (
    CompetitionInfo,
    CompetitionStage,
    CompetitionStatus,
    DiffLap,
    InitialData,
    LengthUnit,
    Participant,
)
from ltspipe.data.enum import ParserSettings
from ltspipe.exceptions import LtsError
from ltspipe.parsers.base import InitialParser
from ltspipe.utils import time_to_millis


class InitialDataParser(InitialParser):
    """
    Parse the initializer data from a websocket.
    """

    FILTER_HEADERS = {
        'by_name': {
            'equipo': ParserSettings.TIMING_NAME,
            'kart': ParserSettings.TIMING_KART_NUMBER,
            '\\u00daltima vuelta': ParserSettings.TIMING_LAST_TIME,
            'mejor vuelta': ParserSettings.TIMING_BEST_TIME,
            'gap': ParserSettings.TIMING_GAP,
            'interv.': ParserSettings.TIMING_INTERVAL,
            'intervalo': ParserSettings.TIMING_INTERVAL,
            'vueltas': ParserSettings.TIMING_LAP,
            'tiempo en pit': ParserSettings.TIMING_PIT_TIME,
            'pits': ParserSettings.TIMING_NUMBER_PITS,
        },
        'by_type': {
            'grp': ParserSettings.IGNORE_GRP,
            'sta': ParserSettings.IGNORE_STA,
            'rk': ParserSettings.TIMING_POSITION,
            'no': ParserSettings.TIMING_KART_NUMBER,
            'dr': ParserSettings.TIMING_NAME,
            'llp': ParserSettings.TIMING_LAST_TIME,
            'blp': ParserSettings.TIMING_BEST_TIME,
            'gap': ParserSettings.TIMING_GAP,
            'int': ParserSettings.TIMING_INTERVAL,
            'pit': ParserSettings.TIMING_NUMBER_PITS,
        },
    }
    FILTER_STAGES = {
        (r'^CRONO', CompetitionStage.QUALIFYING),
        (r'^Entrenos crono', CompetitionStage.QUALIFYING),
        (r'^QUALIFYING', CompetitionStage.QUALIFYING),
        (r'^QUALY', CompetitionStage.QUALIFYING),
        (r'^QUALI', CompetitionStage.QUALIFYING),
        (r'^SUPER-POLE', CompetitionStage.QUALIFYING),
        (r'^RACE', CompetitionStage.RACE),
        (r'^CARRERA', CompetitionStage.RACE),
        (r'^RESISTENCIA', CompetitionStage.RACE),
        (r'^ENDURANCE', CompetitionStage.RACE),
    }

    # The following regex matches the following samples:
    # > '2:12.283'
    # > '00:20:00'
    # > '54.'
    REGEX_TIME = r'^\+?(?:(?:(\d+):)?(\d+):)?(\d+)(?:\.(\d+)?)?$'

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
        if self.is_initializer_data(data):
            parsed_data = self._parse_init_data(data)
            action = Action(
                type=ActionType.INITIALIZE,
                data=parsed_data,
            )
            return [action], True
        return [], False

    def is_initializer_data(self, data: Any) -> bool:
        """Check if it is an initializer data."""
        return (isinstance(data, str)
                and re.match(r'^init\|', data) is not None)

    def _parse_init_data(self, data: str) -> InitialData:
        """Parse content in the raw data."""
        raw_parts = re.split(r'\n+', data, flags=re.MULTILINE)
        raw_parts = [re.split(r'\|', p, flags=re.MULTILINE) for p in raw_parts]
        parts = {p[0]: p for p in raw_parts}

        stage = self._parse_stage(parts['title2'][2])
        remaining_length = self._parse_length(
            parts['dyn1'][1], parts['dyn1'][2])
        status = CompetitionStatus.PAUSED

        # Parse intial content
        raw_content = parts['grid'][2]
        initial_rows = re.findall(r'<tr[^>]*>.+?</tr>', raw_content, flags=re.S)

        headers = self._parse_headers(initial_rows[0])
        participants = self._parse_participants(headers, initial_rows[1:])

        return InitialData(
            stage=stage,
            status=status,
            remaining_length=remaining_length,
            participants=participants,
            parsers_settings=headers,
        )

    def _parse_stage(self, raw: str) -> CompetitionStage:
        """Parse competition stage."""
        for stage_filter in self.FILTER_STAGES:
            stage_regex = stage_filter[0]
            stage = stage_filter[1]
            if re.match(stage_regex, raw):
                return stage
        raise LtsError(f'Unknown stage: {raw}')

    def _parse_length(self, type: str, raw: str) -> DiffLap:
        """Parse remaining length of the competition."""
        if raw == '':
            return DiffLap(
                value=0,
                unit=LengthUnit.MILLIS,
            )
        elif type == 'text':
            return DiffLap(
                value=time_to_millis(raw, default=0),  # type: ignore
                unit=LengthUnit.MILLIS,
            )
        elif type == 'countdown':
            return DiffLap(
                value=int(raw),
                unit=LengthUnit.MILLIS,
            )
        raise LtsError(f'Unknown dyn1 (type={type}, content={raw})')

    def _parse_headers(self, first_row: str) -> Dict[ParserSettings, str]:
        """Parse headers from the first row."""
        header_data: Dict[ParserSettings, str] = {}
        items = re.findall(
            r'<td[^>]*data-id="c(\d+)"[^>]*data-type="([^"]*)"[^>]*>(.*?)</td>',
            first_row,
            flags=re.S)
        for item in items:
            i = int(item[0])
            type_match = self.__get_by_key(
                item[1], self.FILTER_HEADERS['by_type'])
            name_match = self.__get_by_key(
                item[2], self.FILTER_HEADERS['by_name'])

            if type_match is None and name_match is None:
                continue

            if (type_match is not None and (
                    name_match is None or name_match == type_match)):
                header_data[type_match] = f'c{i}'
            elif (name_match is not None and type_match is None):
                header_data[name_match] = f'c{i}'
            else:
                raise LtsError(f'Cannot parse column {i} of headers '
                               f'({type_match} != {name_match}).')

        return header_data

    def _parse_participants(
            self,
            headers: Dict[ParserSettings, str],
            rows: List[str]) -> Dict[str, Participant]:
        """Parse participants details."""
        participants = {}
        for index, row in enumerate(rows):
            items_raw = re.findall(
                r'<td.+?data-id="([^"]+)(c\d+)"[^>]*>(.*?)</td>',
                row,
                flags=re.S)
            items = {item[1]: item for item in items_raw}

            # Check if the row has the team name or the driver name
            has_driver_name = re.match(r'.+drteam.+', row, re.S) is not None

            fields: Dict[ParserSettings, str] = {}
            for field_name, field_column in headers.items():
                item = items[field_column]
                field_value = self._remove_html_tags(item[2])
                if field_name == ParserSettings.TIMING_NAME:
                    field_value = self._clean_participant_name(field_value)
                if field_value != '':
                    fields[field_name] = field_value

            match = re.search(r'<tr[^>]*data-id="([^"]+)"', row, flags=re.S)
            if match is None:
                raise LtsError(f'Could not parse code in: {row}')
            participant_code = match[1]

            match = re.search(r'<tr[^>]*data-pos="([^"]+)"', row, flags=re.S)
            position = None if match is None else str(match[1])

            participants[participant_code] = self._create_participant(
                index=index,
                participant_code=participant_code,
                position=position,
                fields=fields,
                has_driver_name=has_driver_name,
            )

        return participants

    def _clean_participant_name(self, text: str) -> str:
        """
        Clean the name of the participant.

        Given "DIMAS [1:00]", it removes the time.
        """
        matches = re.match(
            r'^(.+?)( \[\d+:\d+\])?$', text)
        if matches is None:
            return ''
        return matches[1]

    def _remove_html_tags(self, text: str) -> str:
        """Remove HTML tags from a string."""
        return re.sub('<[^>]+>', '', text)

    def _parse_diff_lap(
            self,
            diff_lap: Optional[str],
            default: Optional[int] = None) -> Optional[DiffLap]:
        """Parse the difference between laps."""
        if diff_lap is None:
            if default is None:
                return None
            return DiffLap(
                value=default,
                unit=LengthUnit.MILLIS,
            )

        diff_lap = diff_lap.strip()
        match_laps = re.search(
            r'^\+?(\d+) (?:vueltas?|laps?)$', diff_lap.lower())
        if match_laps:
            return DiffLap(
                value=int(match_laps[1]),
                unit=LengthUnit.LAPS,
            )

        diff_value = time_to_millis(diff_lap, default=default)
        if diff_value is not None:
            return DiffLap(
                value=diff_value,
                unit=LengthUnit.MILLIS,
            )

        return None

    def _cast_number(
            self,
            value: Optional[str],
            default: Optional[int] = None) -> Optional[int]:
        """Cast a string to int."""
        return default if value is None else int(value)

    def _create_participant(
            self,
            index: int,
            participant_code: str,
            position: Optional[str],
            fields: Dict[ParserSettings, str],
            has_driver_name: bool) -> Participant:
        """Create instance of participant."""
        default_name = f'Team {index + 1}'
        if has_driver_name:
            team_name = default_name
            driver_name = fields.get(ParserSettings.TIMING_NAME, None)
        else:
            team_name = fields.get(ParserSettings.TIMING_NAME, default_name)
            driver_name = None

        return Participant(
            best_time=time_to_millis(  # type: ignore
                fields.get(ParserSettings.TIMING_BEST_TIME, None),
                default=0),
            driver_name=driver_name,
            gap=self._parse_diff_lap(
                fields.get(ParserSettings.TIMING_GAP, None),
                default=None),
            interval=self._parse_diff_lap(
                fields.get(ParserSettings.TIMING_INTERVAL, None),
                default=None),
            kart_number=self._cast_number(  # type: ignore
                fields.get(ParserSettings.TIMING_KART_NUMBER, None),
                default=0),
            laps=self._cast_number(  # type: ignore
                fields.get(ParserSettings.TIMING_LAP, None),
                default=0),
            last_time=time_to_millis(  # type: ignore
                fields.get(ParserSettings.TIMING_LAST_TIME, None),
                default=0),
            number_pits=self._cast_number(  # type: ignore
                fields.get(ParserSettings.TIMING_NUMBER_PITS, '0'),
                default=0),
            participant_code=participant_code,
            position=self._cast_number(  # type: ignore
                position,
                default=0),
            team_name=team_name,
            pit_time=time_to_millis(
                fields.get(ParserSettings.TIMING_PIT_TIME, None),
                default=None),
        )

    def __get_by_key(
            self,
            value: str,
            filters: Dict[str, ParserSettings]) -> Optional[ParserSettings]:
        """Get by key."""
        value = value.lower()
        if value in filters:
            return filters[value]
        return None

import re
from typing import Any, Dict, List, Optional

from ltspipe.data.actions import Action, ActionType
from ltspipe.data.competitions import (
    DiffLap,
    InitialData,
    LengthUnit,
    Participant,
)
from ltspipe.data.enum import (
    CompetitionStage,
    CompetitionStatus,
    ParserSettings,
)
from ltspipe.parsers.base import Parser


class WsInitParser(Parser):
    """
    Parse the initializer data from a websocket.
    """

    FILTER_HEADERS = {
        'by_id': {
            'rk': ParserSettings.TIMING_RANKING,
            'no': ParserSettings.TIMING_KART_NUMBER,
            'dr': ParserSettings.TIMING_NAME,
            'llp': ParserSettings.TIMING_LAST_LAP_TIME,
            'blp': ParserSettings.TIMING_BEST_TIME,
            'gap': ParserSettings.TIMING_GAP,
            'int': ParserSettings.TIMING_INTERVAL,
            'pit': ParserSettings.TIMING_PITS,
        },
        'by_name': {
            'equipo': ParserSettings.TIMING_NAME,
            'kart': ParserSettings.TIMING_KART_NUMBER,
            '\\u00daltima vuelta': ParserSettings.TIMING_LAST_LAP_TIME,
            'mejor vuelta': ParserSettings.TIMING_BEST_TIME,
            'gap': ParserSettings.TIMING_GAP,
            'interv.': ParserSettings.TIMING_INTERVAL,
            'intervalo': ParserSettings.TIMING_INTERVAL,
            'vueltas': ParserSettings.TIMING_LAPS,
            'tiempo en pit': ParserSettings.TIMING_PIT_TIME,
            'pits': ParserSettings.TIMING_PITS,
        },
    }
    FILTER_STAGES = {
        'CRONO': CompetitionStage.QUALIFYING,
        'QUALIFYING': CompetitionStage.QUALIFYING,
        'QUALY': CompetitionStage.QUALIFYING,
        'QUALI': CompetitionStage.QUALIFYING,
        'RACE': CompetitionStage.RACE,
        'CARRERA': CompetitionStage.RACE,
        'RESISTENCIA': CompetitionStage.RACE,
        'ENDURANCE': CompetitionStage.RACE,
    }

    # The following regex matches the following samples:
    # > '2:12.283'
    # > '00:20:00'
    # > '54.'
    REGEX_TIME = r'^\+?(?:(?:(\d+):)?(\d+):)?(\d+)(?:\.(\d+)?)?$'

    def parse(self, data: Any) -> List[Action]:
        """
        Analyse and/or parse a given data.

        Params:
            data (Any): Data to parse.

        Returns:
            List[Action]: list of actions and their respective parsed data.
        """
        if self._is_initializer_data(data):
            parsed_data = self._parse_init_data(data)
            action = Action(
                type=ActionType.INITIALIZE, data=parsed_data.dict())
            return [action]
        return []

    def _is_initializer_data(self, data: Any) -> bool:
        """Check if it is an initializer data."""
        return (isinstance(data, str)
                and re.match(r'^init\|p\|', data) is not None)

    def _parse_init_data(self, data: str) -> InitialData:
        """Parse content in the raw data."""
        raw_parts = re.split(r'\n+', data, flags=re.MULTILINE)
        raw_parts = [re.split(r'\|', p, flags=re.MULTILINE) for p in raw_parts]
        parts = {p[0]: p for p in raw_parts}

        stage = self._parse_stage(parts['title2'][2])
        remaining_length = self._parse_length(parts['dyn1'][2])
        status = (CompetitionStatus.ONGOING if remaining_length.value > 0
                  else CompetitionStatus.FINISHED)

        # Parse intial content
        raw_content = parts['grid'][2]
        initial_rows = re.findall(r'<tr[^>]*>.+?</tr>', raw_content, flags=re.S)

        headers = self._parse_headers(initial_rows[0])
        participants = self._parse_participants(headers, initial_rows[1:])

        return InitialData(
            reference_time=0,
            reference_current_offset=0,
            stage=stage,
            status=status,
            remaining_length=remaining_length,
            participants=participants,
            parsers_settings=headers,
        )

    def _parse_stage(self, raw: str) -> str:
        """Parse competition stage."""
        if raw in self.FILTER_STAGES:
            return self.FILTER_STAGES[raw]
        raise Exception(f'Unknown stage: {raw}')

    def _parse_length(self, raw: str) -> DiffLap:
        """Parse remaining length of the competition."""
        return DiffLap(
            value=self._time_to_millis(raw),
            unit=LengthUnit.MILLIS,
        )

    def _parse_headers(self, first_row: str) -> Dict[ParserSettings, str]:
        """Parse headers from the first row."""
        header_data = {}
        items = re.findall(
            r'<td[^>]*data-type="([^"]+)"[^>]*>(.*?)</td>',
            first_row,
            flags=re.S)
        for i, item in enumerate(items):
            id_match = self.__get_by_key(
                item[0], self.FILTER_HEADERS['by_id'])
            name_match = self.__get_by_key(
                item[1], self.FILTER_HEADERS['by_name'])

            if id_match is None and name_match is None:
                continue
            if id_match is not None and name_match is None:
                header_data[id_match] = f'c{i + 1}'
            elif id_match is None and name_match is not None:
                header_data[name_match] = f'c{i + 1}'
            elif (id_match is not None
                    and name_match is not None
                    and id_match == name_match):
                header_data[id_match] = f'c{i + 1}'
            else:
                raise Exception(f'Cannot parse column {i + 1} of headers '
                                f'({id_match} != {name_match}).')

        return header_data

    def _parse_participants(
            self,
            headers: Dict[ParserSettings, str],
            rows: List[str]) -> Dict[str, Participant]:
        """Parse participants details."""
        participants = {}
        for row in rows:
            items_raw = re.findall(
                r'<td.+?data-id="([^"]+)(c\d+)"[^>]*>(.*?)</td>',
                row,
                flags=re.S)
            items = {item[1]: item for item in items_raw}

            fields: Dict[ParserSettings, str] = {}
            for field_name, field_column in headers.items():
                item = items[field_column]
                field_value = self._remove_html_tags(item[2])
                if field_value != '':
                    fields[field_name] = field_value

            match = re.search(r'<tr[^>]*data-id="([^"]+)"', row, flags=re.S)
            if match is None:
                raise Exception(f'Could not parse code in: {row}')
            participant_code = match[1]

            match = re.search(r'<tr[^>]*data-pos="([^"]+)"', row, flags=re.S)
            ranking = None if match is None else str(match[1])

            participants[participant_code] = self._create_participant(
                participant_code=participant_code,
                ranking=ranking,
                fields=fields,
            )

        return participants

    def _remove_html_tags(self, text: str) -> str:
        """Remove HTML tags from a string."""
        return re.sub('<[^>]+>', '', text)

    def _time_to_millis(self, lap_time: Optional[str]) -> Optional[int]:
        """Transform a lap time into milliseconds."""
        if lap_time is None:
            return None
        lap_time = lap_time.strip()
        match = re.search(self.REGEX_TIME, lap_time)
        if match is None:
            return None
        else:
            parts = [int(p) if p else 0 for p in match.groups()]
            return (parts[0] * 3600000
                + parts[1] * 60000
                + parts[2] * 1000
                + parts[3])

    def _parse_diff_lap(self, diff_lap: Optional[str]) -> Optional[DiffLap]:
        """Parse the difference between laps."""
        if diff_lap is None:
            return None
        diff_lap = diff_lap.strip()
        match_laps = re.search(
            r'^\+?(\d+) (?:vueltas?|laps?)$', diff_lap.lower())
        if match_laps:
            return DiffLap(
                value=int(match_laps[1]),
                unit=LengthUnit.LAPS,
            )

        diff_value = self._time_to_millis(diff_lap)
        if diff_value is not None:
            return DiffLap(
                value=diff_value,
                unit=LengthUnit.MILLIS,
            )

        return None

    def _cast_number(self, value: Optional[str]) -> Optional[int]:
        """Cast a string to int."""
        return None if value is None else int(value)

    def _create_participant(
            self,
            participant_code: str,
            ranking: Optional[str],
            fields: Dict[ParserSettings, str]) -> Participant:
        """Create instance of participant."""
        return Participant(
            participant_code=participant_code,
            ranking=self._cast_number(ranking),
            kart_number=self._cast_number(fields.get(
                ParserSettings.TIMING_KART_NUMBER, None)),
            team_name=fields.get(
                ParserSettings.TIMING_NAME, None),
            driver_name=None,
            last_lap_time=self._time_to_millis(fields.get(
                ParserSettings.TIMING_LAST_LAP_TIME, None)),
            best_time=self._time_to_millis(fields.get(
                ParserSettings.TIMING_BEST_TIME, None)),
            gap=self._parse_diff_lap(fields.get(
                ParserSettings.TIMING_GAP, None)),
            interval=self._parse_diff_lap(fields.get(
                ParserSettings.TIMING_INTERVAL, None)),
            laps=self._cast_number(fields.get(
                ParserSettings.TIMING_LAPS, None)),
            pits=self._cast_number(fields.get(
                ParserSettings.TIMING_PITS, None)),
            pit_time=self._time_to_millis(fields.get(
                ParserSettings.TIMING_PIT_TIME, None)),
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

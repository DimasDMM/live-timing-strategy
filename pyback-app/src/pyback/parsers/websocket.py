import re
from typing import Dict, List, Optional

from pyback.messages import Message
from pyback.parsers.base import Parser
from pyback.data.time import DiffLap, Unit
from pyback.data.event import InitialData, Participant


class WsInitParser(Parser):
    """
    Parse the initial message in a websocket.
    """

    def __init__(self) -> None:
        """Construct."""
        self._filters = {
            'by_id': {
                'rk': 'RANKING',
                'no': 'KART_NUMBER',
                'dr': 'NAME',
                'llp': 'LAST_LAP_TIME',
                'blp': 'BEST_TIME',
                'gap': 'GAP',
                'int': 'INTERVAL',
                'pit': 'PITS',
            },
            'by_name': {
                'equipo': 'NAME',
                'kart': 'KART_NUMBER',
                '\\u00daltima vuelta': 'LAST_LAP_TIME',
                'mejor vuelta': 'BEST_TIME',
                'gap': 'GAP',
                'interv.': 'INTERVAL',
                'intervalo': 'INTERVAL',
                'vueltas': 'LAPS',
                'tiempo en pit': 'PIT_TIME',
                'pits': 'PITS',
            },
        }

    def parse(self, msg: Message) -> Optional[Message]:
        """
        Parse a given message.

        Params:
            msg (Message): Message to parse.

        Returns:
            Message: transformed message or None if no transformation can be
                applied.
        """
        if self._is_init_msg(msg):
            parsed_data = self._parse_init_data(msg.get_data())
            return Message(
                competition_code=msg.get_competition_code(),
                data=parsed_data,
                source=msg.get_source(),
                created_at=msg.get_created_at(),
                updated_at=msg.get_updated_at(),
                error_description=msg.get_error_description(),
                error_traceback=msg.get_error_traceback(),
            )
        return None

    def _is_init_msg(self, msg: Message) -> bool:
        """Check if it is an initializer message."""
        data = msg.get_data()
        return (isinstance(data, str)
                and re.match(r'^init\|p\|', data) is not None)

    def _parse_init_data(self, data: str) -> dict:
        """Parse content in the raw data."""
        parts = re.split(r'\|', data)

        # Parse race stage
        race_part = parts[24]
        race_part = re.sub('\n.+', '', race_part, flags=re.MULTILINE)

        # Parse intial content
        raw_content = parts[40]
        initial_rows = re.findall(r'<tr[^>]*>.+?</tr>', raw_content, flags=re.S)

        headers = self._parse_headers(initial_rows[0])
        participants = self._parse_participants(headers, initial_rows[1:])

        initial_data = InitialData(headers=headers, participants=participants)
        return initial_data.to_dict()

    def _parse_headers(self, first_row: str) -> Dict[str, str]:
        """Parse headers from the first row."""
        header_data = {}
        items = re.findall(
            r'<td[^>]*data-type="([^"]+)"[^>]*>(.*?)</td>',
            first_row,
            flags=re.S)
        for i, item in enumerate(items):
            id_match = self.__get_by_key(item[0], self._filters['by_id'])
            name_match = self.__get_by_key(item[1], self._filters['by_name'])

            if id_match is None and name_match is None:
                continue
            if id_match is not None and name_match is None:
                header_data[f'c{i + 1}'] = id_match
            elif id_match is None and name_match is not None:
                header_data[f'c{i + 1}'] = name_match
            elif (id_match is not None
                    and name_match is not None
                    and id_match == name_match):
                header_data[f'c{i + 1}'] = id_match
            else:
                raise Exception(f'Cannot parse column {i + 1} of headers '
                                f'({id_match} != {name_match}).')

        return header_data

    def __get_by_key(
            self,
            value: str,
            filters: Dict[str, str]) -> Optional[str]:
        """Get by key."""
        value = value.lower()
        if value in filters:
            return filters[value]
        return None

    def _parse_participants(
            self,
            headers: Dict[str, str],
            rows: List[str]) -> Dict[str, Participant]:
        """Parse participants details."""
        participants = {}
        for row in rows:
            items = re.findall(
                r'<td.+?data-id="([^"]+)(c\d+)"[^>]*>(.*?)</td>',
                row,
                flags=re.S)
            fields = {}
            for item in items:
                if item[1] not in headers:
                    continue
                field_name = headers[item[1]]
                field_value = self._remove_html_tags(item[2])
                fields[field_name] = None if field_value == '' else field_value

            match = re.search(r'<tr[^>]*data-id="([^"]+)"', row, flags=re.S)
            if match is None:
                raise Exception(f'Could not parse code in: {row}')
            code = match[1]

            match = re.search(r'<tr[^>]*data-pos="([^"]+)"', row, flags=re.S)
            ranking = None if match is None else match[1]

            p = Participant(
                code=code,
                ranking=self._cast_number(ranking),
                kart_number=self._cast_number(fields.get('KART_NUMBER', None)),
                team_name=fields.get('NAME', None),
                driver_name=None,
                last_lap_time=self._time_to_millis(
                    fields.get('LAST_LAP_TIME', None)),
                best_time=self._time_to_millis(fields.get('BEST_TIME', None)),
                gap=self._parse_diff_lap(fields.get('GAP', None)),
                interval=self._parse_diff_lap(fields.get('INTERVAL', None)),
                laps=self._cast_number(fields.get('LAPS', None)),
                pits=self._cast_number(fields.get('PITS', None)),
                pit_time=self._time_to_millis(fields.get('PIT_TIME', None)),
            )
            participants[code] = p

        return participants

    def _remove_html_tags(self, text: str) -> str:
        """Remove HTML tags from a string."""
        return re.sub('<[^>]+>', '', text)

    def _time_to_millis(self, lap_time: Optional[str]) -> Optional[int]:
        """Transform a lap time into milliseconds."""
        if lap_time is None:
            return None
        lap_time = lap_time.strip()
        match = re.search(r'^\+?(?:(\d+):)?(\d+)\.(\d+)?$', lap_time)
        if match is None:
            return None
        else:
            parts = [int(p) if p else 0 for p in match.groups()]
            return parts[0] * 60000 + parts[1] * 1000 + parts[2]

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
                unit=Unit.LAPS,
            )

        diff_value = self._time_to_millis(diff_lap)
        if diff_value is not None:
            return DiffLap(
                value=diff_value,
                unit=Unit.MILLIS,
            )

        return None

    def _cast_number(self, value: Optional[str]) -> Optional[int]:
        """Cast a string to int."""
        return None if value is None else int(value)

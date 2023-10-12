import re
from typing import Optional

from ltspipe.data.competitions import (
    CompetitionInfo,
    Driver,
    Team,
)
from ltspipe.data.enum import ParserSettings
from ltspipe.exceptions import LtsError


# The following regex matches the following samples:
# > '2:12.283'
# > '00:20:00'
# > '54.'
REGEX_TIME = r'^\+?(?:(?:(\d+):)?(\d+):)?(\d+)(?:\.(\d+)?)?$'


def find_driver_by_id(
        info: CompetitionInfo,
        driver_id: int) -> Optional[Driver]:
    """Find a driver in the competition info."""
    for d in info.drivers:
        if d.id == driver_id:
            return d
    return None


def find_driver_by_name(
        info: CompetitionInfo,
        participant_code: str,
        driver_name: str) -> Optional[Driver]:
    """Find a driver in the competition info."""
    for d in info.drivers:
        if d.name == driver_name and d.participant_code == participant_code:
            return d
    return None


def find_team_by_code(
        info: CompetitionInfo,
        participant_code: str) -> Optional[Team]:
    """Find a team in the competition info."""
    return info.teams.get(participant_code, None)


def find_team_by_id(
        info: CompetitionInfo,
        team_id: int) -> Optional[Team]:
    """Find a team in the competition info."""
    for _, t in info.teams.items():
        if t.id == team_id:
            return t
    return None


def time_to_millis(
        str_time: Optional[str],
        default: Optional[int] = None) -> Optional[int]:
    """Transform a lap time into milliseconds."""
    if str_time is None:
        return default
    str_time = str_time.strip()
    match = re.search(REGEX_TIME, str_time)
    if match is None:
        return default
    else:
        parts = [int(p) if p else 0 for p in match.groups()]
        return (parts[0] * 3600000
            + parts[1] * 60000
            + parts[2] * 1000
            + parts[3])


def is_column_parser_setting(
        info: CompetitionInfo,
        column_id: str,
        parser_setting: ParserSettings,
        raise_exception: bool = True) -> bool:
    """Validate that the column correspond to the expected data."""
    if parser_setting in info.parser_settings:
        name_id = info.parser_settings[parser_setting]
        return name_id == column_id

    if raise_exception:
        raise LtsError(f'Column for {parser_setting} not found')

    return False

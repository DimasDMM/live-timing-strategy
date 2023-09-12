from typing import Dict, Optional

from ltspipe.data.competitions import (
    CompetitionInfo,
    Driver,
    Team,
)
from ltspipe.data.enum import ParserSettings


def _find_driver_by_name(
        competitions: Dict[str, CompetitionInfo],
        competition_code: str,
        driver_name: str) -> Optional[Driver]:
    """Find a driver in the competition info."""
    info = competitions[competition_code]
    for d in info.drivers:
        if d.name == driver_name:
            return d
    return None


def _find_team_by_code(
        competitions: Dict[str, CompetitionInfo],
        competition_code: str,
        team_code: str) -> Optional[Team]:
    """Find a team in the competition info."""
    info = competitions[competition_code]
    for t in info.teams:
        if t.participant_code == team_code:
            return t
    return None


def _is_column_parser_setting(
        competitions: Dict[str, CompetitionInfo],
        competition_code: str,
        column_id: str,
        parser_setting: ParserSettings) -> bool:
    """Validate that the column correspond to the expected data."""
    info = competitions[competition_code]
    if parser_setting in info.parser_settings:
        name_id = info.parser_settings[parser_setting]
        return name_id == column_id

    raise Exception(f'Column for {parser_setting} not found')

from typing import Dict, Optional

from ltspipe.data.competitions import (
    CompetitionInfo,
    Driver,
    Team,
)


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

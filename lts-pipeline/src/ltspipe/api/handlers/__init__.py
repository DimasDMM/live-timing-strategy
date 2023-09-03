from typing import Optional

from ltspipe.data.competitions import (
    CompetitionInfo,
    Driver,
    Team,
)


def _find_driver_by_name(
        info: CompetitionInfo,
        participant_code: str,
        driver_name: str) -> Optional[Driver]:
    """Find a driver in the competition info."""
    for d in info.drivers:
        if d.name == driver_name and d.participant_code == participant_code:
            return d
    return None


def _find_driver_by_id(
        info: CompetitionInfo,
        participant_code: str,
        driver_id: int) -> Optional[Driver]:
    """Find a driver in the competition info."""
    for d in info.drivers:
        if d.id == driver_id and d.participant_code == participant_code:
            return d
    return None


def _find_team_by_code(
        info: CompetitionInfo,
        participant_code: str) -> Optional[Team]:
    """Find a team in the competition info."""
    for t in info.teams:
        if t.participant_code == participant_code:
            return t
    return None


def _find_team_by_id(
        info: CompetitionInfo,
        participant_code: str,
        team_id: int) -> Optional[Team]:
    """Find a team in the competition info."""
    for t in info.teams:
        if t.id == team_id and t.participant_code == participant_code:
            return t
    return None

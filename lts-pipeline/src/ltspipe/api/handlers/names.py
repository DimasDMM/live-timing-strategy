from typing import Dict, Optional

from ltspipe.api.handlers.base import ApiHandler
from ltspipe.api.participants import (
    add_driver,
    add_team,
    update_driver,
    update_team,
)
from ltspipe.base import BaseModel
from ltspipe.data.auth import AuthData
from ltspipe.data.competitions import (
    CompetitionInfo,
    Driver,
    Team,
    UpdateDriver,
    UpdateTeam,
)


class UpdateDriverHandler(ApiHandler):
    """Handle UpdateDriver instances."""

    def __init__(
            self,
            api_url: str,
            auth_data: AuthData,
            competitions: Dict[str, CompetitionInfo]) -> None:
        """Construct."""
        self._api_url = api_url
        self._auth_data = auth_data
        self._competitions = competitions

    def handle(self, model: BaseModel) -> None:
        """Update the data of a driver."""
        if not isinstance(model, UpdateDriver):
            raise Exception('The model must be an instance of UpdateDriver.')

        competition_code = model.competition_code
        info = self._competitions[competition_code]
        old_driver = self._find_driver(
            competition_code=model.competition_code,
            driver_name=model.name)

        if old_driver is None:
            # Add new driver
            new_driver = add_driver(
                api_url=self._api_url,
                bearer=self._auth_data.bearer,
                competition_id=info.id,  # type: ignore
                participant_code=model.participant_code,
                name=model.name,
                number=model.number,
                team_id=model.team_id,
            )
            info.drivers.append(new_driver)
        elif old_driver.name != model.name or old_driver.number != model.number:
            # Update driver name if needed
            updated_driver = update_driver(
                self._api_url,
                bearer=self._auth_data.bearer,
                competition_id=info.id,  # type: ignore
                driver_id=model.id,  # type: ignore
                participant_code=model.participant_code,
                name=model.name,
                number=model.number,
            )
            old_driver.name = updated_driver.name
            old_driver.number = updated_driver.number

    def _find_driver(
            self,
            competition_code: str,
            driver_name: str) -> Optional[Driver]:
        """Find a driver in the competition info."""
        info = self._competitions[competition_code]
        for d in info.drivers:
            if d.name == driver_name:
                return d
        return None


class UpdateTeamHandler(ApiHandler):
    """Handle UpdateTeam instances."""

    def __init__(
            self,
            api_url: str,
            auth_data: AuthData,
            competitions: Dict[str, CompetitionInfo]) -> None:
        """Construct."""
        self._api_url = api_url
        self._auth_data = auth_data
        self._competitions = competitions

    def handle(self, model: BaseModel) -> None:
        """Update the data of a team."""
        if not isinstance(model, UpdateTeam):
            raise Exception('The model must be an instance of UpdateTeam.')

        competition_code = model.competition_code
        info = self._competitions[competition_code]
        old_team = self._find_team(
            competition_code=model.competition_code,
            participant_code=model.participant_code)

        if old_team is None:
            # Add new team
            new_team = add_team(
                api_url=self._api_url,
                bearer=self._auth_data.bearer,
                competition_id=info.id,  # type: ignore
                participant_code=model.participant_code,
                name=model.name,
                number=model.number,
            )
            info.teams.append(new_team)
        elif old_team.name != model.name or old_team.number != model.number:
            # Update team name if needed
            updated_team = update_team(
                self._api_url,
                bearer=self._auth_data.bearer,
                competition_id=info.id,  # type: ignore
                team_id=model.id,  # type: ignore
                participant_code=model.participant_code,
                name=model.name,
                number=model.number,
            )
            old_team.name = updated_team.name
            old_team.number = updated_team.number

    def _find_team(
            self,
            competition_code: str,
            participant_code: str) -> Optional[Team]:
        """Find a team in the competition info."""
        info = self._competitions[competition_code]
        for t in info.teams:
            if t.participant_code == participant_code:
                return t
        return None

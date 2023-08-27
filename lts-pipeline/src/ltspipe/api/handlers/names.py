from typing import Dict, Optional

from ltspipe.api.handlers.base import ApiHandler
from ltspipe.api.participants import (
    add_driver,
    add_team,
    get_team_driver_by_name,
    get_team_by_code,
    update_driver,
    update_team,
)
from ltspipe.base import BaseModel
from ltspipe.data.auth import AuthData
from ltspipe.data.notifications import Notification, NotificationType
from ltspipe.data.competitions import (
    CompetitionInfo,
    Driver,
    Team,
    UpdateDriver,
    UpdateTeam,
)


def _find_driver(
        info: CompetitionInfo,
        participant_code: str,
        driver_name: str) -> Optional[Driver]:
    """Find a driver in the competition info."""
    for d in info.drivers:
        if d.name == driver_name and d.participant_code == participant_code:
            return d
    return None


def _find_team(
        info: CompetitionInfo,
        participant_code: str) -> Optional[Team]:
    """Find a team in the competition info."""
    for t in info.teams:
        if t.participant_code == participant_code:
            return t
    return None


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

    def handle(self, model: BaseModel) -> Optional[Notification]:
        """Update the data of a driver."""
        if not isinstance(model, UpdateDriver):
            raise Exception('The model must be an instance of UpdateDriver.')

        competition_code = model.competition_code
        info = self._competitions[competition_code]
        old_driver = _find_driver(info, model.participant_code, model.name)

        if old_driver is None:
            # Check if the driver exists in the API
            old_driver = self._update_driver_in_info(
                info, model.team_id, model.name)

        if old_driver is None:
            # Add new driver
            current_driver = add_driver(
                api_url=self._api_url,
                bearer=self._auth_data.bearer,
                competition_id=info.id,  # type: ignore
                participant_code=model.participant_code,
                name=model.name,
                number=model.number,
                team_id=model.team_id,
            )
            info.drivers.append(current_driver)
        elif old_driver.name != model.name or old_driver.number != model.number:
            # Update driver name if needed
            current_driver = update_driver(
                self._api_url,
                bearer=self._auth_data.bearer,
                competition_id=info.id,  # type: ignore
                driver_id=model.id,  # type: ignore
                participant_code=model.participant_code,
                name=model.name,
                number=model.number,
            )
            old_driver.name = current_driver.name
            old_driver.number = current_driver.number
        else:
            # The driver already exists, so do nothing
            return None

        return self._create_notification(current_driver)

    def _create_notification(self, driver: Driver) -> Notification:
        """Create notification of handler."""
        return Notification(
            type=NotificationType.UPDATED_DRIVER,
            data=driver,
        )

    def _update_driver_in_info(
            self,
            info: CompetitionInfo,
            team_id: int,
            driver_name: str) -> Optional[Driver]:
        """Update driver by its name in the competition info."""
        driver = get_team_driver_by_name(
            self._api_url,
            self._auth_data.bearer,
            info.id,  # type: ignore
            team_id,
            driver_name)
        if driver is None:
            return None

        info.drivers.append(driver)
        return driver


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

    def handle(self, model: BaseModel) -> Optional[Notification]:
        """Update the data of a team."""
        if not isinstance(model, UpdateTeam):
            raise Exception('The model must be an instance of UpdateTeam.')

        competition_code = model.competition_code
        info = self._competitions[competition_code]
        old_team = _find_team(info, participant_code=model.participant_code)

        if old_team is None:
            # Check if the team exists in the API
            old_team = self._update_team_in_info(
                info, model.participant_code)

        if old_team is None:
            # Add new team
            current_team = add_team(
                api_url=self._api_url,
                bearer=self._auth_data.bearer,
                competition_id=info.id,  # type: ignore
                participant_code=model.participant_code,
                name=model.name,
                number=model.number,
            )
            info.teams.append(current_team)
        elif old_team.name != model.name or old_team.number != model.number:
            # Update team name if needed
            current_team = update_team(
                self._api_url,
                bearer=self._auth_data.bearer,
                competition_id=info.id,  # type: ignore
                team_id=model.id,  # type: ignore
                participant_code=model.participant_code,
                name=model.name,
                number=model.number,
            )
            old_team.name = current_team.name
            old_team.number = current_team.number
        else:
            # The team already exists, so do nothing
            return None

        return self._create_notification(current_team)

    def _create_notification(self, team: Team) -> Notification:
        """Create notification of handler."""
        return Notification(
            type=NotificationType.UPDATED_TEAM,
            data=team,
        )

    def _update_team_in_info(
            self,
            info: CompetitionInfo,
            participant_code: str) -> Optional[Team]:
        """Update team by its name in the competition info."""
        team = get_team_by_code(
            self._api_url,
            self._auth_data.bearer,
            info.id,  # type: ignore
            participant_code)
        if team is None:
            return None

        info.teams.append(team)
        return team

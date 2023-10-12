from typing import Optional

from ltspipe.utils import (
    find_driver_by_id,
    find_driver_by_name,
    find_team_by_code,
)
from ltspipe.api.handlers.base import ApiHandler
from ltspipe.api.participants import (
    add_driver,
    add_team,
    update_driver,
    update_driver_partial_driving_time,
    update_team,
)
from ltspipe.api.pits import (
    get_last_pit_out_by_team,
    update_pit_out_driver_by_id,
)
from ltspipe.api.timing import update_timing_driver_by_team
from ltspipe.data.base import BaseModel
from ltspipe.data.auth import AuthData
from ltspipe.data.notifications import Notification, NotificationType
from ltspipe.data.competitions import (
    CompetitionInfo,
    Driver,
    Team,
    UpdateDriver,
    UpdateDriverPartialDrivingTime,
    UpdateTeam,
)
from ltspipe.exceptions import LtsError


class UpdateDriverHandler(ApiHandler):
    """Handle UpdateDriver instances."""

    def __init__(
            self,
            api_url: str,
            auth_data: AuthData,
            info: CompetitionInfo) -> None:
        """Construct."""
        self._api_url = api_url
        self._auth_data = auth_data
        self._info = info

    def handle(self, model: BaseModel) -> Optional[Notification]:
        """Update the data of a driver."""
        if not isinstance(model, UpdateDriver):
            raise LtsError('The model must be an instance of UpdateDriver.')

        if model.id is None:
            old_driver = find_driver_by_name(
                self._info, model.participant_code, model.name)
        else:
            old_driver = find_driver_by_id(
                self._info, model.id)
            if old_driver is None:
                raise LtsError(f'Unknown driver to update: {model}')

        if old_driver is None:
            # Add new driver
            current_driver = add_driver(
                api_url=self._api_url,
                bearer=self._auth_data.bearer,
                competition_id=self._info.id,
                participant_code=model.participant_code,
                name=model.name,
                number=model.number,
                team_id=model.team_id,
            )
            self._info.drivers.append(current_driver)
        elif old_driver.name != model.name or old_driver.number != model.number:
            # Update driver name if needed
            current_driver = update_driver(
                self._api_url,
                bearer=self._auth_data.bearer,
                competition_id=self._info.id,
                driver_id=model.id,  # type: ignore
                participant_code=model.participant_code,
                name=model.name,
                number=model.number,
            )
            old_driver.name = current_driver.name
            old_driver.number = current_driver.number
        else:
            # Ignore driver
            return None

        # Update driver ID in the timing and in the last pit-out
        self._update_timing_with_driver_id(
            competition_id=self._info.id,
            team_id=model.team_id,
            driver_id=current_driver.id,
        )
        self._update_pit_out_with_driver_id(
            competition_id=self._info.id,
            team_id=model.team_id,
            driver_id=current_driver.id,
        )

        return self._create_notification(current_driver)

    def _create_notification(self, driver: Driver) -> Notification:
        """Create notification of handler."""
        return Notification(
            type=NotificationType.UPDATED_DRIVER,
            data=driver,
        )

    def _update_timing_with_driver_id(
            self,
            competition_id: int,
            team_id: int,
            driver_id: int) -> None:
        """Update the timing of the team with the Driver ID."""
        timing = update_timing_driver_by_team(
            api_url=self._api_url,
            bearer=self._auth_data.bearer,
            competition_id=competition_id,
            team_id=team_id,
            driver_id=driver_id,
        )
        self._info.timing[timing.participant_code] = timing

    def _update_pit_out_with_driver_id(
            self,
            competition_id: int,
            team_id: int,
            driver_id: int) -> None:
        """Update the last pit-out of the team with the Driver ID."""
        last_pit_out = get_last_pit_out_by_team(
            api_url=self._api_url,
            bearer=self._auth_data.bearer,
            competition_id=competition_id,
            team_id=team_id,
        )
        if last_pit_out is not None:
            _ = update_pit_out_driver_by_id(
                api_url=self._api_url,
                bearer=self._auth_data.bearer,
                competition_id=competition_id,
                pit_out_id=last_pit_out.id,
                driver_id=driver_id,
            )


class UpdateDriverPartialDrivingTimeHandler(ApiHandler):
    """Handle UpdateDriverPartialDrivingTime instances."""

    def __init__(
            self,
            api_url: str,
            auth_data: AuthData,
            info: CompetitionInfo) -> None:
        """Construct."""
        self._api_url = api_url
        self._auth_data = auth_data
        self._info = info

    def handle(self, model: BaseModel) -> Optional[Notification]:
        """Update the data of a driver."""
        if not isinstance(model, UpdateDriverPartialDrivingTime):
            raise LtsError('The model must be an instance of '
                           'UpdateDriverPartialDrivingTime.')

        new_driver = update_driver_partial_driving_time(
            api_url=self._api_url,
            bearer=self._auth_data.bearer,
            competition_id=self._info.id,
            driver_id=model.id,
            partial_driving_time=model.partial_driving_time,
            auto_compute_total=model.auto_compute_total,
        )

        old_driver = find_driver_by_id(info=self._info, driver_id=model.id)
        if old_driver is None:
            self._info.drivers.append(new_driver)
        else:
            old_driver.partial_driving_time = new_driver.partial_driving_time
            old_driver.total_driving_time = new_driver.total_driving_time

        return self._create_notification(new_driver)

    def _create_notification(self, driver: Driver) -> Notification:
        """Create notification of handler."""
        return Notification(
            type=NotificationType.UPDATED_DRIVER_PARTIAL_DRIVING_TIME,
            data=driver,
        )


class UpdateTeamHandler(ApiHandler):
    """Handle UpdateTeam instances."""

    def __init__(
            self,
            api_url: str,
            auth_data: AuthData,
            info: CompetitionInfo) -> None:
        """Construct."""
        self._api_url = api_url
        self._auth_data = auth_data
        self._info = info

    def handle(self, model: BaseModel) -> Optional[Notification]:
        """Update the data of a team."""
        if not isinstance(model, UpdateTeam):
            raise LtsError('The model must be an instance of UpdateTeam.')

        old_team: Optional[Team] = find_team_by_code(
            info=self._info,
            participant_code=model.participant_code)

        if old_team is None:
            # Add new team
            current_team = add_team(
                api_url=self._api_url,
                bearer=self._auth_data.bearer,
                competition_id=self._info.id,
                participant_code=model.participant_code,
                name=model.name,
                number=model.number,
            )
            self._info.teams[current_team.participant_code] = current_team
        elif old_team.name != model.name or old_team.number != model.number:
            # Update team name if needed
            current_team = update_team(
                self._api_url,
                bearer=self._auth_data.bearer,
                competition_id=self._info.id,
                team_id=old_team.id,
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

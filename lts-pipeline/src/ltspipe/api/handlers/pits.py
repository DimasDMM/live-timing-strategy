from typing import Optional

from ltspipe.api.handlers.base import ApiHandler
from ltspipe.api.timing import (
    get_timing_by_team,
    update_timing_driver_by_team,
    update_timing_pit_time_by_team,
)
from ltspipe.api.pits import (
    add_pit_in,
    add_pit_out,
)
from ltspipe.base import BaseModel
from ltspipe.data.auth import AuthData
from ltspipe.data.notifications import Notification, NotificationType
from ltspipe.data.competitions import (
    CompetitionInfo,
    KartStatus,
    AddPitIn,
    AddPitOut,
    PitIn,
    PitOut,
)
from ltspipe.exceptions import LtsError


class AddPitInHandler(ApiHandler):
    """Handle AddPitIn instances."""

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
        """Add the data of a pit-in."""
        if not isinstance(model, AddPitIn):
            raise LtsError('The model must be an instance of AddPitIn.')

        # Get latest information about the timing of the team
        last_timing = get_timing_by_team(
            api_url=self._api_url,
            bearer=self._auth_data.bearer,
            competition_id=self._info.id,
            team_id=model.team_id,
        )
        if last_timing is None:
            lap = 0
            driver_id = None
            kart_status = KartStatus.UNKNOWN
            fixed_kart_status = None
            pit_time = 0
        else:
            lap = 0 if last_timing.lap is None else last_timing.lap
            driver_id = last_timing.driver_id
            kart_status = last_timing.kart_status
            fixed_kart_status = last_timing.fixed_kart_status
            pit_time = (last_timing.pit_time
                        if last_timing.pit_time is not None else 0)

        # Add pit-in
        new_pit_in = add_pit_in(
            api_url=self._api_url,
            bearer=self._auth_data.bearer,
            competition_id=self._info.id,
            kart_status=kart_status,
            fixed_kart_status=fixed_kart_status,
            pit_time=pit_time,
            lap=lap,
            driver_id=driver_id,
            team_id=model.team_id,
        )

        return self._create_notification(new_pit_in)

    def _create_notification(self, pit_in: PitIn) -> Notification:
        """Create notification of handler."""
        return Notification(
            type=NotificationType.ADDED_PIT_IN,
            data=pit_in,
        )


class AddPitOutHandler(ApiHandler):
    """Handle AddPitOut instances."""

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
        """Add the data of a pit-out."""
        if not isinstance(model, AddPitOut):
            raise LtsError('The model must be an instance of AddPitOut.')

        # Add pit-out
        new_pit_out = add_pit_out(
            api_url=self._api_url,
            bearer=self._auth_data.bearer,
            competition_id=self._info.id,
            kart_status=KartStatus.UNKNOWN,
            driver_id=None,
            team_id=model.team_id,
        )

        # Clean pit-time and driver in the timing information
        _ = update_timing_driver_by_team(
            api_url=self._api_url,
            bearer=self._auth_data.bearer,
            competition_id=self._info.id,
            team_id=model.team_id,
            driver_id=None,
        )
        _ = update_timing_pit_time_by_team(
            api_url=self._api_url,
            bearer=self._auth_data.bearer,
            competition_id=self._info.id,
            team_id=model.team_id,
            pit_time=None,
        )

        return self._create_notification(new_pit_out)

    def _create_notification(self, pit_out: PitOut) -> Notification:
        """Create notification of handler."""
        return Notification(
            type=NotificationType.ADDED_PIT_OUT,
            data=pit_out,
        )

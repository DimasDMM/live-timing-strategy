from typing import Dict, Optional

from ltspipe.api.handlers.base import ApiHandler
from ltspipe.api.pits import (
    add_pit_in,
    add_pit_out,
)
from ltspipe.base import BaseModel
from ltspipe.data.auth import AuthData
from ltspipe.data.notifications import Notification, NotificationType
from ltspipe.data.competitions import (
    CompetitionInfo,
    AddPitIn,
    AddPitOut,
    PitIn,
    PitOut,
)


class AddPitInHandler(ApiHandler):
    """Handle AddPitIn instances."""

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
        """Add the data of a pit-in."""
        if not isinstance(model, AddPitIn):
            raise Exception('The model must be an instance of AddPitIn.')

        competition_code = model.competition_code
        info = self._competitions[competition_code]

        # Add pit-in
        new_pit_in = add_pit_in(
            api_url=self._api_url,
            bearer=self._auth_data.bearer,
            competition_id=info.id,  # type: ignore
            kart_status=model.kart_status,
            pit_time=model.pit_time,
            lap=model.lap,
            driver_id=model.driver_id,
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
            competitions: Dict[str, CompetitionInfo]) -> None:
        """Construct."""
        self._api_url = api_url
        self._auth_data = auth_data
        self._competitions = competitions

    def handle(self, model: BaseModel) -> Optional[Notification]:
        """Add the data of a pit-out."""
        if not isinstance(model, AddPitOut):
            raise Exception('The model must be an instance of AddPitOut.')

        competition_code = model.competition_code
        info = self._competitions[competition_code]

        # Add pit-out
        new_pit_out = add_pit_out(
            api_url=self._api_url,
            bearer=self._auth_data.bearer,
            competition_id=info.id,  # type: ignore
            kart_status=model.kart_status,
            driver_id=model.driver_id,
            team_id=model.team_id,
        )

        return self._create_notification(new_pit_out)

    def _create_notification(self, pit_out: PitOut) -> Notification:
        """Create notification of handler."""
        return Notification(
            type=NotificationType.ADDED_PIT_OUT,
            data=pit_out,
        )
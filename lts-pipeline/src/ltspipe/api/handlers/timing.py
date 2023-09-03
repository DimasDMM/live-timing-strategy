from typing import Dict, Optional

from ltspipe.api.handlers.base import ApiHandler
from ltspipe.api.timing import update_timing_position_by_team
from ltspipe.base import BaseModel
from ltspipe.data.auth import AuthData
from ltspipe.data.notifications import Notification, NotificationType
from ltspipe.data.competitions import (
    CompetitionInfo,
    ParticipantTiming,
    UpdateTimingPosition,
)


class UpdateTimingPositionHandler(ApiHandler):
    """Handle UpdateTimingPosition instances."""

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
        """Update the timing position of a participant."""
        if not isinstance(model, UpdateTimingPosition):
            raise Exception(
                'The model must be an instance of UpdateTimingPosition.')

        competition_code = model.competition_code
        info = self._competitions[competition_code]

        participant_timing = update_timing_position_by_team(
            api_url=self._api_url,
            bearer=self._auth_data.bearer,
            competition_id=info.id,  # type: ignore
            team_id=model.team_id,
            position=model.position,
            auto_other_positions=model.auto_other_positions,
        )

        return self._create_notification(participant_timing)

    def _create_notification(self, data: ParticipantTiming) -> Notification:
        """Create notification of handler."""
        return Notification(
            type=NotificationType.UPDATED_TIMING_POSITION,
            data=data,
        )

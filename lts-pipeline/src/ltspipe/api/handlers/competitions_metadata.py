from typing import Dict, Optional

from ltspipe.api.handlers.base import ApiHandler
from ltspipe.api.competitions_base import (
    update_competition_metadata_status,
)
from ltspipe.base import BaseModel
from ltspipe.data.auth import AuthData
from ltspipe.data.notifications import Notification, NotificationType
from ltspipe.data.competitions import (
    CompetitionInfo,
    UpdateCompetitionMetadataStatus,
)


class UpdateCompetitionMetadataStatusHandler(ApiHandler):
    """Handle CompetitionMetadataStatus instances."""

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
        if not isinstance(model, UpdateCompetitionMetadataStatus):
            raise Exception(
                'The model must be an instance of CompetitionMetadataStatus.')

        competition_code = model.competition_code
        info = self._competitions[competition_code]

        update_competition_metadata_status(
            api_url=self._api_url,
            bearer=self._auth_data.bearer,
            competition_id=info.id,  # type: ignore
            status=model.status,
        )

        return self._create_notification(model)

    def _create_notification(
            self,
            metadata_status: UpdateCompetitionMetadataStatus) -> Notification:
        """Create notification of handler."""
        return Notification(
            type=NotificationType.UPDATE_COMPETITION_METADATA_STATUS,
            data=metadata_status,
        )

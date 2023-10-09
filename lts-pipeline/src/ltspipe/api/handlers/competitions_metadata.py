from typing import Optional

from ltspipe.api.handlers.base import ApiHandler
from ltspipe.api.competitions_base import (
    update_competition_metadata_remaining,
    update_competition_metadata_status,
)
from ltspipe.base import BaseModel
from ltspipe.data.auth import AuthData
from ltspipe.data.notifications import Notification, NotificationType
from ltspipe.data.competitions import (
    CompetitionInfo,
    CompetitionMetadata,
    CompetitionStatus,
    UpdateCompetitionMetadataRemaining,
    UpdateCompetitionMetadataStatus,
)


class UpdateCompetitionMetadataRemainingHandler(ApiHandler):
    """Handle CompetitionMetadataRemaining instances."""

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
        if not isinstance(model, UpdateCompetitionMetadataRemaining):
            raise Exception(
                'The model must be an instance of '
                'CompetitionMetadataRemaining.')

        competition_metadata = update_competition_metadata_remaining(
            api_url=self._api_url,
            bearer=self._auth_data.bearer,
            competition_id=self._info.id,
            remaining_length=model.remaining_length,
        )

        return self._create_notification(competition_metadata)

    def _create_notification(
        self,
        competition_metadata: CompetitionMetadata,
    ) -> Notification:
        """Create notification of handler."""
        return Notification(
            type=NotificationType.UPDATED_COMPETITION_METADATA_REMAINING,
            data=competition_metadata,
        )


class UpdateCompetitionMetadataStatusHandler(ApiHandler):
    """Handle CompetitionMetadataStatus instances."""

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
        if not isinstance(model, UpdateCompetitionMetadataStatus):
            raise Exception(
                'The model must be an instance of CompetitionMetadataStatus.')

        competition_metadata = update_competition_metadata_status(
            api_url=self._api_url,
            bearer=self._auth_data.bearer,
            competition_id=self._info.id,
            status=model.status,
        )

        # Additionally, update remaining length to zero if status is finished
        if model.status == CompetitionStatus.FINISHED:
            remaining_length = competition_metadata.remaining_length
            remaining_length.value = 0
            competition_metadata = update_competition_metadata_remaining(
                api_url=self._api_url,
                bearer=self._auth_data.bearer,
                competition_id=self._info.id,
                remaining_length=remaining_length,
            )

        return self._create_notification(competition_metadata)

    def _create_notification(
            self,
            competition_metadata: CompetitionMetadata) -> Notification:
        """Create notification of handler."""
        return Notification(
            type=NotificationType.UPDATED_COMPETITION_METADATA_STATUS,
            data=competition_metadata,
        )

import pytest

from ltspipe.api.auth import refresh_bearer
from ltspipe.api.competitions_base import build_competition_info
from ltspipe.api.handlers.competitions_metadata import (
    UpdateCompetitionMetadataRemainingHandler,
    UpdateCompetitionMetadataStatusHandler,
)
from ltspipe.data.competitions import (
    CompetitionMetadata,
    CompetitionStage,
    CompetitionStatus,
    DiffLap,
    LengthUnit,
    UpdateCompetitionMetadataRemaining,
    UpdateCompetitionMetadataStatus,
)
from ltspipe.data.notifications import Notification, NotificationType
from tests.fixtures import AUTH_KEY, REAL_API_LTS
from tests.helpers import DatabaseTest


class TestUpdateCompetitionMetadataRemainingHandler(DatabaseTest):
    """
    Functional test of ltspipe.api.handlers.UpdateCompetitionMetadataRemainin...

    Important: Since these tests are functional, they require that there are
    a database and an API REST running.
    """

    @pytest.mark.parametrize(
        ('competition_code', 'update_data', 'expected_notification'),
        [
            (
                'south-endurance-2023-03-26',  # competition_code
                UpdateCompetitionMetadataRemaining(  # update_data
                    competition_code='south-endurance-2023-03-26',
                    remaining_length=DiffLap(
                        value=1200000,
                        unit=LengthUnit.MILLIS,
                    ),
                ),
                Notification(  # expected_notification
                    type=NotificationType.UPDATED_COMPETITION_METADATA_REMAINING,  # noqa: E501, LN001
                    data=CompetitionMetadata(
                        stage=CompetitionStage.FREE_PRACTICE,
                        status=CompetitionStatus.PAUSED,
                        remaining_length=DiffLap(
                            value=1200000,
                            unit=LengthUnit.MILLIS,
                        ),
                    ),
                ),
            ),
        ],
    )
    def test_handle(
            self,
            competition_code: str,
            update_data: UpdateCompetitionMetadataRemaining,
            expected_notification: Notification) -> None:
        """Test handle method."""
        auth_data = refresh_bearer(REAL_API_LTS, AUTH_KEY)
        info = build_competition_info(
            REAL_API_LTS,
            bearer=auth_data.bearer,
            competition_code=competition_code)
        competitions = {competition_code: info}

        # Handle method
        handler = UpdateCompetitionMetadataRemainingHandler(
            api_url=REAL_API_LTS,
            auth_data=auth_data,
            competitions=competitions)
        notification = handler.handle(update_data)
        assert notification is not None
        assert notification.dict() == expected_notification.dict()


class TestUpdateCompetitionMetadataStatusHandler(DatabaseTest):
    """
    Functional test of ltspipe.api.handlers.UpdateCompetitionMetadataStatusHa...

    Important: Since these tests are functional, they require that there are
    a database and an API REST running.
    """

    @pytest.mark.parametrize(
        ('competition_code', 'update_data', 'expected_notification'),
        [
            (
                'south-endurance-2023-03-26',  # competition_code
                UpdateCompetitionMetadataStatus(  # update_data
                    competition_code='south-endurance-2023-03-26',
                    status=CompetitionStatus.ONGOING,
                ),
                Notification(  # expected_notification
                    type=NotificationType.UPDATED_COMPETITION_METADATA_STATUS,
                    data=CompetitionMetadata(
                        stage=CompetitionStage.FREE_PRACTICE,
                        status=CompetitionStatus.ONGOING,
                        remaining_length=DiffLap(
                            value=1200000,
                            unit=LengthUnit.MILLIS,
                        ),
                    ),
                ),
            ),
            (
                'south-endurance-2023-03-26',  # competition_code
                UpdateCompetitionMetadataStatus(  # update_data
                    competition_code='south-endurance-2023-03-26',
                    status=CompetitionStatus.FINISHED,
                ),
                Notification(  # expected_notification
                    type=NotificationType.UPDATED_COMPETITION_METADATA_STATUS,
                    data=CompetitionMetadata(
                        stage=CompetitionStage.FREE_PRACTICE,
                        status=CompetitionStatus.FINISHED,
                        remaining_length=DiffLap(
                            value=0,
                            unit=LengthUnit.MILLIS,
                        ),
                    ),
                ),
            ),
        ],
    )
    def test_handle(
            self,
            competition_code: str,
            update_data: UpdateCompetitionMetadataStatus,
            expected_notification: Notification) -> None:
        """Test handle method."""
        auth_data = refresh_bearer(REAL_API_LTS, AUTH_KEY)
        info = build_competition_info(
            REAL_API_LTS,
            bearer=auth_data.bearer,
            competition_code=competition_code)
        competitions = {competition_code: info}

        # Handle method
        handler = UpdateCompetitionMetadataStatusHandler(
            api_url=REAL_API_LTS,
            auth_data=auth_data,
            competitions=competitions)
        notification = handler.handle(update_data)
        assert notification is not None
        assert notification.dict() == expected_notification.dict()

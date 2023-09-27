import pytest
from typing import Dict

from ltspipe.api.auth import refresh_bearer
from ltspipe.api.competitions_base import build_competition_info
from ltspipe.api.handlers.competitions_metadata import (
    UpdateCompetitionMetadataRemainingHandler,
    UpdateCompetitionMetadataStatusHandler,
)
from ltspipe.data.competitions import (
    CompetitionInfo,
    CompetitionMetadata,
    CompetitionStage,
    CompetitionStatus,
    DiffLap,
    LengthUnit,
    UpdateCompetitionMetadataRemaining,
    UpdateCompetitionMetadataStatus,
)
from ltspipe.data.notifications import Notification, NotificationType
from tests.fixtures import AUTH_KEY, REAL_API_LTS, TEST_COMPETITION_CODE
from tests.helpers import (
    DatabaseTest,
    DatabaseContent,
    TableContent,
)


class TestUpdateCompetitionMetadataRemainingHandler(DatabaseTest):
    """
    Functional test of ltspipe.api.handlers.UpdateCompetitionMetadataRemainin...

    Important: Since these tests are functional, they require that there are
    a database and an API REST running.
    """

    @pytest.mark.parametrize(
        ('database_content, in_competitions, update_data,'
         'expected_notification, expected_database'),
        [
            (
                DatabaseContent(  # database_content
                    tables_content=[
                        TableContent(
                            table_name='competitions_index',
                            columns=[
                                'track_id',
                                'competition_code',
                                'name',
                                'description',
                            ],
                            content=[
                                [
                                    1,
                                    TEST_COMPETITION_CODE,
                                    'Endurance North 26-02-2023',
                                    'Endurance in Karting North',
                                ],
                            ],
                        ),
                        TableContent(
                            table_name='competitions_metadata_current',
                            columns=[
                                'competition_id',
                                'reference_time',
                                'reference_current_offset',
                                'status',
                                'stage',
                                'remaining_length',
                                'remaining_length_unit',
                            ],
                            content=[
                                [
                                    1,
                                    None,
                                    None,
                                    'paused',
                                    'free-practice',
                                    0,
                                    'millis'
                                ],
                            ],
                        ),
                    ],
                ),
                {  # in_competitions
                    TEST_COMPETITION_CODE: CompetitionInfo(
                        id=1,
                        competition_code=TEST_COMPETITION_CODE,
                        parser_settings={},
                        drivers=[],
                        teams=[],
                    ),
                },
                UpdateCompetitionMetadataRemaining(  # update_data
                    competition_code=TEST_COMPETITION_CODE,
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
                DatabaseContent(  # expected_database
                    tables_content=[
                        TableContent(
                            table_name='competitions_metadata_current',
                            columns=[
                                'competition_id',
                                'reference_time',
                                'reference_current_offset',
                                'status',
                                'stage',
                                'remaining_length',
                                'remaining_length_unit',
                            ],
                            content=[
                                [
                                    1,
                                    None,
                                    None,
                                    'paused',
                                    'free-practice',
                                    1200000,
                                    'millis'
                                ],
                            ],
                        ),
                    ],
                ),
            ),
        ],
    )
    def test_handle(
            self,
            database_content: DatabaseContent,
            in_competitions: Dict[str, CompetitionInfo],
            update_data: UpdateCompetitionMetadataRemaining,
            expected_notification: Notification,
            expected_database: DatabaseContent) -> None:
        """Test handle method."""
        self.set_database_content(database_content)
        auth_data = refresh_bearer(REAL_API_LTS, AUTH_KEY)

        # Handle method
        handler = UpdateCompetitionMetadataRemainingHandler(
            api_url=REAL_API_LTS,
            auth_data=auth_data,
            competitions=in_competitions)
        notification = handler.handle(update_data)
        assert notification is not None
        assert notification.model_dump() == expected_notification.model_dump()

        # Validate database content
        query = expected_database.to_query()
        assert (self.get_database_content(query).model_dump() ==
                expected_database.model_dump())


class TestUpdateCompetitionMetadataStatusHandler(DatabaseTest):
    """
    Functional test of ltspipe.api.handlers.UpdateCompetitionMetadataStatusHa...

    Important: Since these tests are functional, they require that there are
    a database and an API REST running.
    """

    @pytest.mark.parametrize(
        ('database_content, in_competitions, update_data,'
         'expected_notification, expected_database'),
        [
            (
                DatabaseContent(  # database_content
                    tables_content=[
                        TableContent(
                            table_name='competitions_index',
                            columns=[
                                'track_id',
                                'competition_code',
                                'name',
                                'description',
                            ],
                            content=[
                                [
                                    1,
                                    TEST_COMPETITION_CODE,
                                    'Endurance North 26-02-2023',
                                    'Endurance in Karting North',
                                ],
                            ],
                        ),
                        TableContent(
                            table_name='competitions_metadata_current',
                            columns=[
                                'competition_id',
                                'reference_time',
                                'reference_current_offset',
                                'status',
                                'stage',
                                'remaining_length',
                                'remaining_length_unit',
                            ],
                            content=[
                                [
                                    1,
                                    None,
                                    None,
                                    'paused',
                                    'free-practice',
                                    0,
                                    'millis'
                                ],
                            ],
                        ),
                    ],
                ),
                {  # in_competitions
                    TEST_COMPETITION_CODE: CompetitionInfo(
                        id=1,
                        competition_code=TEST_COMPETITION_CODE,
                        parser_settings={},
                        drivers=[],
                        teams=[],
                    ),
                },
                UpdateCompetitionMetadataStatus(  # update_data
                    competition_code=TEST_COMPETITION_CODE,
                    status=CompetitionStatus.ONGOING,
                ),
                Notification(  # expected_notification
                    type=NotificationType.UPDATED_COMPETITION_METADATA_STATUS,
                    data=CompetitionMetadata(
                        stage=CompetitionStage.FREE_PRACTICE,
                        status=CompetitionStatus.ONGOING,
                        remaining_length=DiffLap(
                            value=0,
                            unit=LengthUnit.MILLIS,
                        ),
                    ),
                ),
                DatabaseContent(  # expected_database
                    tables_content=[
                        TableContent(
                            table_name='competitions_metadata_current',
                            columns=[
                                'competition_id',
                                'reference_time',
                                'reference_current_offset',
                                'status',
                                'stage',
                                'remaining_length',
                                'remaining_length_unit',
                            ],
                            content=[
                                [
                                    1,
                                    None,
                                    None,
                                    'ongoing',
                                    'free-practice',
                                    0,
                                    'millis'
                                ],
                            ],
                        ),
                    ],
                ),
            ),
            (
                DatabaseContent(  # database_content
                    tables_content=[
                        TableContent(
                            table_name='competitions_index',
                            columns=[
                                'track_id',
                                'competition_code',
                                'name',
                                'description',
                            ],
                            content=[
                                [
                                    1,
                                    TEST_COMPETITION_CODE,
                                    'Endurance North 26-02-2023',
                                    'Endurance in Karting North',
                                ],
                            ],
                        ),
                        TableContent(
                            table_name='competitions_metadata_current',
                            columns=[
                                'competition_id',
                                'reference_time',
                                'reference_current_offset',
                                'status',
                                'stage',
                                'remaining_length',
                                'remaining_length_unit',
                            ],
                            content=[
                                [
                                    1,
                                    None,
                                    None,
                                    'paused',
                                    'free-practice',
                                    0,
                                    'millis'
                                ],
                            ],
                        ),
                    ],
                ),
                {  # in_competitions
                    TEST_COMPETITION_CODE: CompetitionInfo(
                        id=1,
                        competition_code=TEST_COMPETITION_CODE,
                        parser_settings={},
                        drivers=[],
                        teams=[],
                    ),
                },
                UpdateCompetitionMetadataStatus(  # update_data
                    competition_code=TEST_COMPETITION_CODE,
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
                DatabaseContent(  # expected_database
                    tables_content=[
                        TableContent(
                            table_name='competitions_metadata_current',
                            columns=[
                                'competition_id',
                                'reference_time',
                                'reference_current_offset',
                                'status',
                                'stage',
                                'remaining_length',
                                'remaining_length_unit',
                            ],
                            content=[
                                [
                                    1,
                                    None,
                                    None,
                                    'finished',
                                    'free-practice',
                                    0,
                                    'millis'
                                ],
                            ],
                        ),
                    ],
                ),
            ),
        ],
    )
    def test_handle(
            self,
            database_content: DatabaseContent,
            in_competitions: Dict[str, CompetitionInfo],
            update_data: UpdateCompetitionMetadataStatus,
            expected_notification: Notification,
            expected_database: DatabaseContent) -> None:
        """Test handle method."""
        self.set_database_content(database_content)
        auth_data = refresh_bearer(REAL_API_LTS, AUTH_KEY)

        # Handle method
        handler = UpdateCompetitionMetadataStatusHandler(
            api_url=REAL_API_LTS,
            auth_data=auth_data,
            competitions=in_competitions)
        notification = handler.handle(update_data)
        assert notification is not None
        assert notification.model_dump() == expected_notification.model_dump()

        # Validate database content
        query = expected_database.to_query()
        assert (self.get_database_content(query).model_dump() ==
                expected_database.model_dump())

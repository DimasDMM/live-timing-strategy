from datetime import datetime
import pytest
from unittest.mock import MagicMock

from ltspipe.api.auth import refresh_bearer
from ltspipe.api.handlers.base import ApiHandler
from ltspipe.data.actions import Action, ActionType
from ltspipe.data.competitions import (
    CompetitionInfo,
    CompetitionStage,
    CompetitionStatus,
    DiffLap,
    Driver,
    InitialData,
    KartStatus,
    Participant,
    ParserSettings,
    Team,
    Timing,
)
from ltspipe.data.enum import LengthUnit
from ltspipe.data.notifications import Notification, NotificationType
from ltspipe.messages import Message, MessageDecoder, MessageSource
from ltspipe.steps.api import (
    ApiActionStep,
    CompetitionInfoRefreshStep,
)
from ltspipe.steps.base import MidStep
from tests.fixtures import API_LTS, AUTH_KEY, TEST_COMPETITION_CODE
from tests.helpers import (
    DatabaseTest,
    DatabaseContent,
    TableContent,
)
from tests.mocks.logging import FakeLogger


class TestApiActionStep:
    """Test ltspipe.steps.api.ApiActionStep class."""

    @pytest.mark.parametrize(
        ('message, expected_notification'),
        [
            (
                Message(  # message
                    competition_code=TEST_COMPETITION_CODE,
                    data=Action(
                        type=ActionType.INITIALIZE,
                        data=InitialData(
                            competition_code=TEST_COMPETITION_CODE,
                            stage=CompetitionStage.QUALIFYING.value,
                            status=CompetitionStatus.ONGOING.value,
                            remaining_length=DiffLap(
                                value=1200000,
                                unit=LengthUnit.MILLIS,
                            ),
                            parsers_settings={},
                            participants={
                                'r5625': Participant(
                                    best_time=64882,  # 1:04.882
                                    driver_name=None,
                                    gap=DiffLap(
                                        value=0,
                                        unit=LengthUnit.MILLIS,
                                    ),
                                    interval=DiffLap(
                                        value=0,
                                        unit=LengthUnit.MILLIS,
                                    ),
                                    kart_number=1,
                                    laps=5,
                                    last_time=65142,  # 1:05.142
                                    number_pits=0,
                                    participant_code='r5625',
                                    pit_time=None,
                                    position=1,
                                    team_name='Team 1',
                                ),
                            },
                        ),
                    ),
                    source=MessageSource.SOURCE_WS_LISTENER,
                    decoder=MessageDecoder.ACTION,
                    created_at=datetime.utcnow().timestamp(),
                    updated_at=datetime.utcnow().timestamp(),
                ),
                Notification(  # expected_notification
                    type=NotificationType.INIT_FINISHED,
                ),
            ),
        ],
    )
    def test_run_step(
            self,
            message: Message,
            expected_notification: Notification) -> None:
        """Test run_step method."""
        # Create mocks
        next_step = MagicMock()
        next_step.get_children.return_value = []
        notification_step = MagicMock()
        notification_step.get_children.return_value = []
        handler = MagicMock()
        handler.handle.return_value = expected_notification

        # Create step and call method
        step = self._build_step(handler, notification_step, next_step)
        step.run_step(message)

        # Do validations
        assert next_step.run_step.call_count == 1
        received_msg: Message = next_step.run_step.call_args_list[0][0][0]
        assert received_msg.competition_code == TEST_COMPETITION_CODE
        assert received_msg.data == message.data

        assert notification_step.run_step.call_count == 1
        notification_msg: Message = (
            notification_step.run_step.call_args_list[0][0][0])
        assert notification_msg.competition_code == TEST_COMPETITION_CODE
        assert notification_msg.data == expected_notification

        # Also, check that the get_children method returns the mocks
        children = step.get_children()
        assert children == [next_step, notification_step]

    def _build_step(
            self,
            handler: ApiHandler,
            notification_step: MidStep,
            next_step: MidStep) -> ApiActionStep:
        """Build step to test."""
        in_competition = CompetitionInfo(
            id=1,
            competition_code=TEST_COMPETITION_CODE,
            parser_settings={},
            drivers=[],
            teams={},
            timing={},
        )
        fake_logger = FakeLogger()
        step = ApiActionStep(
            logger=fake_logger,
            api_lts=API_LTS,
            info=in_competition,
            action_handlers={
                ActionType.INITIALIZE: handler,
            },
            notification_step=notification_step,
            next_step=next_step,
        )
        return step


class TestCompetitionInfoRefreshStep(DatabaseTest):
    """Test ltspipe.steps.api.CompetitionInfoRefreshStep class."""

    DATABASE_CONTENT = DatabaseContent(
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
                        'millis',
                    ],
                ],
            ),
            TableContent(
                table_name='parsers_settings',
                columns=[
                    'competition_id',
                    'name',
                    'value',
                ],
                content=[
                    [1, 'timing-name', 'sample-name'],
                    [1, 'timing-position', 'sample-position'],
                ],
            ),
            TableContent(
                table_name='participants_teams',
                columns=[
                    'competition_id',
                    'participant_code',
                    'name',
                    'number',
                    'reference_time_offset',
                ],
                content=[
                    [1, 'r5625', 'Team 1', 41, None],
                ],
            ),
            TableContent(
                table_name='participants_drivers',
                columns=[
                    'competition_id',
                    'team_id',
                    'participant_code',
                    'name',
                    'number',
                    'total_driving_time',
                    'partial_driving_time',
                    'reference_time_offset',
                ],
                content=[
                    [
                        1,
                        1,
                        'r5625',
                        'Team 1 Driver 1',
                        41,
                        0,
                        0,
                        None,
                    ],
                    [
                        1,
                        1,
                        'r5625',
                        'Team 1 Driver 2',
                        41,
                        0,
                        0,
                        None,
                    ],
                ],
            ),
            TableContent(
                table_name='timing_current',
                columns=[
                    'competition_id',
                    'team_id',
                    'driver_id',
                    'position',
                    'last_time',
                    'best_time',
                    'lap',
                    'gap',
                    'gap_unit',
                    'interval',
                    'interval_unit',
                    'stage',
                    'pit_time',
                    'kart_status',
                    'fixed_kart_status',
                    'number_pits',
                ],
                content=[
                    [
                        1,  # competition_id
                        1,  # team_id
                        1,  # driver_id
                        1,  # position
                        61000,  # last_time
                        51000,  # best_time
                        3,  # lap
                        None,  # gap
                        None,  # gap_unit
                        0,  # interval
                        'millis',  # interval_unit
                        'free-practice',  # stage
                        0,  # pit_time
                        'good',  # kart_status
                        None,  # fixed_kart_status
                        2,  # number_pits
                    ],
                ],
            ),
        ],
    )
    EXPECTED_COMPETITION = CompetitionInfo(
        id=1,
        competition_code=TEST_COMPETITION_CODE,
        drivers=[
            Driver(
                id=1,
                team_id=1,
                participant_code='r5625',
                name='Team 1 Driver 1',
                number=41,
                total_driving_time=0,
                partial_driving_time=0,
            ),
            Driver(
                id=2,
                team_id=1,
                participant_code='r5625',
                name='Team 1 Driver 2',
                number=41,
                total_driving_time=0,
                partial_driving_time=0,
            ),
        ],
        teams={
            'r5625': Team(
                id=1,
                participant_code='r5625',
                name='Team 1',
                number=41,
            ),
        },
        parser_settings={
            ParserSettings.TIMING_NAME: 'sample-name',
            ParserSettings.TIMING_POSITION: 'sample-position',
        },
        timing={
            'r5625': Timing(
                best_time=51000,
                driver_id=1,
                fixed_kart_status=None,
                gap=None,
                interval=DiffLap(value=0, unit=LengthUnit.MILLIS),
                kart_status=KartStatus.GOOD,
                lap=3,
                last_time=61000,
                number_pits=2,
                participant_code='r5625',
                pit_time=0,
                position=1,
                stage=CompetitionStage.FREE_PRACTICE,
                team_id=1,
            ),
        },
    )

    def test_run_step(
            self,
            sample_message: Message) -> None:
        """Test method run_step."""
        self.set_database_content(self.DATABASE_CONTENT)
        auth_data = refresh_bearer(API_LTS, AUTH_KEY)

        competition_code = sample_message.competition_code

        # Create a mock of the next step
        next_step = MagicMock()
        next_step.get_children.return_value = []

        # Create step
        in_competition = CompetitionInfo(
            id=1,
            competition_code=TEST_COMPETITION_CODE,
            parser_settings={},
            drivers=[],
            teams={},
            timing={},
        )
        fake_logger = FakeLogger()
        step = CompetitionInfoRefreshStep(
            logger=fake_logger,
            api_lts=API_LTS,
            auth_data=auth_data,
            info=in_competition,
            next_step=next_step,
        )

        # Run step and validate that the competition info is retrieved
        step.run_step(sample_message)
        assert in_competition == self.EXPECTED_COMPETITION

        assert next_step.run_step.call_count == 1
        received_msg: Message = next_step.run_step.call_args_list[0][0][0]
        assert received_msg.competition_code == competition_code
        assert received_msg.data == sample_message.data

        # Also, check that the get_children method returns the mocks
        children = step.get_children()
        assert children == [next_step]

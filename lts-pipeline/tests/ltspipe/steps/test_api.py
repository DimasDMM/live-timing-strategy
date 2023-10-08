from datetime import datetime
import pytest
from pytest_mock import MockerFixture
from typing import Dict, List
from unittest.mock import MagicMock

from ltspipe.api.handlers.base import ApiHandler
from ltspipe.data.auth import AuthData
from ltspipe.data.actions import Action, ActionType
from ltspipe.data.competitions import (
    CompetitionInfo,
    CompetitionStage,
    CompetitionStatus,
    DiffLap,
    Driver,
    InitialData,
    Participant,
    ParserSettings,
    Team,
)
from ltspipe.data.enum import LengthUnit
from ltspipe.data.notifications import Notification, NotificationType
from ltspipe.messages import Message, MessageDecoder, MessageSource
from ltspipe.steps.api import (
    ApiActionStep,
    CompetitionInfoRefreshStep,
)
from ltspipe.steps.base import MidStep
from tests.conftest import mock_requests
from tests.fixtures import MOCK_API_LTS, TEST_COMPETITION_CODE
from tests.mocks.logging import FakeLogger
from tests.mocks.requests import (
    MapRequestItem,
    MapRequestMethod,
    MockResponse,
)


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
        in_competitions: Dict[str, CompetitionInfo] = {
            TEST_COMPETITION_CODE: CompetitionInfo(
                id=None,
                competition_code=TEST_COMPETITION_CODE,
            ),
        }
        fake_logger = FakeLogger()
        step = ApiActionStep(
            logger=fake_logger,
            api_lts=MOCK_API_LTS,
            competitions=in_competitions,
            action_handlers={
                ActionType.INITIALIZE: handler,
            },
            notification_step=notification_step,
            next_step=next_step,
        )
        return step


class TestCompetitionInfoRefreshStep:
    """Test ltspipe.steps.api.CompetitionInfoRefreshStep class."""

    EXPECTED_COMPETITIONS = {
        TEST_COMPETITION_CODE: CompetitionInfo(
            id=1,
            competition_code=TEST_COMPETITION_CODE,
            drivers=[
                Driver(
                    id=1,
                    team_id=1,
                    participant_code='team-1',
                    name='Team 1 Driver 1',
                    number=41,
                    total_driving_time=0,
                    partial_driving_time=0,
                ),
                Driver(
                    id=2,
                    team_id=1,
                    participant_code='team-1',
                    name='Team 1 Driver 2',
                    number=41,
                    total_driving_time=0,
                    partial_driving_time=0,
                ),
            ],
            teams=[
                Team(
                    id=1,
                    participant_code='team-1',
                    name='Team 1',
                    number=41,
                ),
            ],
            parser_settings={
                ParserSettings.TIMING_NAME: 'sample-name',
                ParserSettings.TIMING_POSITION: 'sample-position',
            },
        ),
    }

    def test_run_step(
            self,
            mocker: MockerFixture,
            sample_auth_data: AuthData,
            sample_message: Message) -> None:
        """Test method run_step."""
        self._apply_mock_api(mocker, MOCK_API_LTS)
        competition_code = sample_message.competition_code

        # Create a mock of the next step
        next_step = MagicMock()
        next_step.get_children.return_value = []

        # Create step
        in_competitions: Dict[str, CompetitionInfo] = {}
        fake_logger = FakeLogger()
        step = CompetitionInfoRefreshStep(
            logger=fake_logger,
            api_lts=MOCK_API_LTS,
            auth_data=sample_auth_data,
            competitions=in_competitions,
            next_step=next_step,
        )

        # Run step and validate that the competition info is retrieved
        step.run_step(sample_message)
        assert in_competitions == self.EXPECTED_COMPETITIONS

        assert next_step.run_step.call_count == 1
        received_msg: Message = next_step.run_step.call_args_list[0][0][0]
        assert received_msg.competition_code == competition_code
        assert received_msg.data == sample_message.data

        # Also, check that the get_children method returns the mocks
        children = step.get_children()
        assert children == [next_step]

    def _apply_mock_api(self, mocker: MockerFixture, api_url: str) -> None:
        """Apply mock to API."""
        api_url = api_url.strip('/')
        requests_map = (
            self._mock_response_get_competition_info(api_url)
            + self._mock_response_get_drivers(api_url)
            + self._mock_response_get_parser_settings(api_url)
            + self._mock_response_get_teams(api_url))
        mock_requests(mocker, requests_map=requests_map)

    def _mock_response_get_competition_info(
            self, api_url: str) -> List[MapRequestItem]:
        """Get mocked response."""
        response = MockResponse(
            content={
                'id': 1,
                'track': {
                    'id': 1,
                    'name': 'Karting North',
                    'insert_date': '2023-04-15T21:43:26',
                    'update_date': '2023-04-15T21:43:26',
                },
                'competition_code': TEST_COMPETITION_CODE,
                'name': 'Endurance North 26-02-2023',
                'description': 'Endurance in Karting North',
                'insert_date': '2023-04-15T21:43:26',
                'update_date': '2023-04-15T21:43:26',
            },
        )
        item = MapRequestItem(
            url=(f'{api_url}/v1/c/'
                 f'filter/code/{TEST_COMPETITION_CODE}'),
            method=MapRequestMethod.GET,
            responses=[response],
        )
        return [item]

    def _mock_response_get_parser_settings(
            self, api_url: str) -> List[MapRequestItem]:
        """Get mocked response."""
        response = MockResponse(
            content=[
                {
                    'name': ParserSettings.TIMING_NAME.value,
                    'value': 'sample-name',
                    'insert_date': '2023-04-15T21:43:26',
                    'update_date': '2023-04-15T21:43:26',
                },
                {
                    'name': ParserSettings.TIMING_POSITION.value,
                    'value': 'sample-position',
                    'insert_date': '2023-04-15T21:43:26',
                    'update_date': '2023-04-15T21:43:26',
                },
            ],
        )
        item = MapRequestItem(
            url=f'{api_url}/v1/c/1/parsers/settings',
            method=MapRequestMethod.GET,
            responses=[response],
        )
        return [item]

    def _mock_response_get_drivers(self, api_url: str) -> List[MapRequestItem]:
        """Get mocked response."""
        response = MockResponse(
            content=[
                {
                    'id': 1,
                    'competition_id': 1,
                    'team_id': 1,
                    'participant_code': 'team-1',
                    'name': 'Team 1 Driver 1',
                    'number': 41,
                    'total_driving_time': 0,
                    'partial_driving_time': 0,
                    'insert_date': '2023-04-20T00:55:35',
                    'update_date': '2023-04-20T00:55:35',
                },
                {
                    'id': 2,
                    'competition_id': 1,
                    'team_id': 1,
                    'participant_code': 'team-1',
                    'name': 'Team 1 Driver 2',
                    'number': 41,
                    'total_driving_time': 0,
                    'partial_driving_time': 0,
                    'insert_date': '2023-04-20T00:55:35',
                    'update_date': '2023-04-20T00:55:35',
                },
            ],
        )
        item = MapRequestItem(
            url=f'{api_url}/v1/c/1/drivers',
            method=MapRequestMethod.GET,
            responses=[response],
        )
        return [item]

    def _mock_response_get_teams(self, api_url: str) -> List[MapRequestItem]:
        """Get mocked response."""
        response = MockResponse(
            content=[
                {
                    'id': 1,
                    'competition_id': 1,
                    'participant_code': 'team-1',
                    'name': 'Team 1',
                    'number': 41,
                    'drivers': [],
                    'insert_date': '2023-04-20T01:30:48',
                    'update_date': '2023-04-20T01:30:48',
                },
            ],
        )
        item = MapRequestItem(
            url=f'{api_url}/v1/c/1/teams',
            method=MapRequestMethod.GET,
            responses=[response],
        )
        return [item]

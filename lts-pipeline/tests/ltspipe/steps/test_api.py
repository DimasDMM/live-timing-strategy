from datetime import datetime
from pytest_mock import MockerFixture
from typing import Dict
from unittest.mock import MagicMock

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
from ltspipe.messages import Message, MessageDecoder, MessageSource
from ltspipe.steps.api import (
    ApiActionStep,
    CompetitionInfoInitStep,
)
from tests.conftest import mock_requests_get
from tests.fixtures import TEST_COMPETITION_CODE
from tests.mocks.logging import FakeLogger


class TestApiActionStep:
    """Test ltspipe.steps.api.ApiActionStep class."""

    API_LTS = 'http://localhost:8090/'
    SAMPLE_MESSAGE = Message(
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
                        participant_code='r5625',
                        ranking=1,
                        kart_number=1,
                        team_name='CKM 1',
                        last_lap_time=65142,  # 1:05.142
                        best_time=64882,  # 1:04.882
                    ),
                },
            ),
        ),
        source=MessageSource.SOURCE_WS_LISTENER,
        decoder=MessageDecoder.ACTION,
        created_at=datetime.utcnow().timestamp(),
        updated_at=datetime.utcnow().timestamp(),
    )

    def test_run_step(self) -> None:
        """Test run_step method."""
        # Create mocks
        next_step = MagicMock()
        next_step.get_children.return_value = []
        handler = MagicMock()

        # Create step
        in_competitions: Dict[str, CompetitionInfo] = {
            TEST_COMPETITION_CODE: CompetitionInfo(
                id=None,
                competition_code=TEST_COMPETITION_CODE,
            ),
        }
        fake_logger = FakeLogger()
        step = ApiActionStep(
            logger=fake_logger,
            api_lts=self.API_LTS,
            competitions=in_competitions,
            action_handlers={
                ActionType.INITIALIZE: handler,
            },
            next_step=next_step,
        )

        # Call method and do validations
        step.run_step(self.SAMPLE_MESSAGE)

        assert next_step.run_step.call_count == 1
        received_msg: Message = next_step.run_step.call_args_list[0][0][0]
        assert received_msg.competition_code == TEST_COMPETITION_CODE
        assert received_msg.data == self.SAMPLE_MESSAGE.data

        # Also, check that the get_children method returns the mocks
        children = step.get_children()
        assert children == [next_step]


class TestParserSettingsGetterStep:
    """Test ltspipe.steps.api.ParserSettingsGetterStep class."""

    API_LTS = 'http://localhost:8090/'
    RESPONSE_LIST_COMPETITIONS = {
        'id': 1,
        'track': {
            'id': 1,
            'name': 'Karting North',
            'insert_date': '2023-04-15T21:43:26',
            'update_date': '2023-04-15T21:43:26',
        },
        'competition_code': 'north-endurance-2023-02-26',
        'name': 'Endurance North 26-02-2023',
        'description': 'Endurance in Karting North',
        'insert_date': '2023-04-15T21:43:26',
        'update_date': '2023-04-15T21:43:26',
    }
    RESPONSE_LIST_SETTINGS = [
        {
            'name': ParserSettings.TIMING_NAME,
            'value': 'sample-name',
            'insert_date': '2023-04-15T21:43:26',
            'update_date': '2023-04-15T21:43:26',
        },
        {
            'name': ParserSettings.TIMING_RANKING,
            'value': 'sample-ranking',
            'insert_date': '2023-04-15T21:43:26',
            'update_date': '2023-04-15T21:43:26',
        },
    ]
    RESPONSE_LIST_DRIVERS = [
        {
            'id': 1,
            'competition_id': 1,
            'team_id': 1,
            'participant_code': 'team-1',
            'name': 'CKM 1 Driver 1',
            'number': 41,
            'total_driving_time': 0,
            'partial_driving_time': 0,
            'reference_time_offset': 0,
            'insert_date': '2023-04-20T00:55:35',
            'update_date': '2023-04-20T00:55:35',
        },
        {
            'id': 2,
            'competition_id': 1,
            'team_id': 1,
            'participant_code': 'team-1',
            'name': 'CKM 1 Driver 2',
            'number': 41,
            'total_driving_time': 0,
            'partial_driving_time': 0,
            'reference_time_offset': 0,
            'insert_date': '2023-04-20T00:55:35',
            'update_date': '2023-04-20T00:55:35',
        },
    ]
    RESPONSE_LIST_TEAMS = [
        {
            'id': 1,
            'competition_id': 1,
            'participant_code': 'team-1',
            'name': 'CKM 1',
            'number': 41,
            'reference_time_offset': 0,
            'drivers': [],
            'insert_date': '2023-04-20T01:30:48',
            'update_date': '2023-04-20T01:30:48',
        },
    ]
    EXPECTED_COMPETITIONS = {
        TEST_COMPETITION_CODE: CompetitionInfo(
            id=1,
            competition_code=TEST_COMPETITION_CODE,
            drivers=[
                Driver(
                    id=1,
                    team_id=1,
                    participant_code='team-1',
                    name='CKM 1 Driver 1',
                ),
                Driver(
                    id=2,
                    team_id=1,
                    participant_code='team-1',
                    name='CKM 1 Driver 2',
                ),
            ],
            teams=[
                Team(
                    id=1,
                    participant_code='team-1',
                    name='CKM 1',
                ),
            ],
            parser_settings={
                ParserSettings.TIMING_NAME: 'sample-name',
                ParserSettings.TIMING_RANKING: 'sample-ranking',
            },
        ),
    }

    def test_run_step(
            self,
            mocker: MockerFixture,
            sample_message: Message) -> None:
        """Test method run_step."""
        self._apply_mock_api(mocker)
        competition_code = sample_message.competition_code

        # Create a mock of the next step
        next_step = MagicMock()
        next_step.get_children.return_value = []

        # Create step
        in_competitions: Dict[str, CompetitionInfo] = {}
        fake_logger = FakeLogger()
        step = CompetitionInfoInitStep(
            logger=fake_logger,
            api_lts=self.API_LTS,
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

    def _apply_mock_api(self, mocker: MockerFixture) -> None:
        """Apply mock to API."""
        responses: list = [
            self.RESPONSE_LIST_COMPETITIONS,
            self.RESPONSE_LIST_SETTINGS,
            self.RESPONSE_LIST_DRIVERS,
            self.RESPONSE_LIST_TEAMS,
        ]
        _ = mock_requests_get(mocker, responses=responses)

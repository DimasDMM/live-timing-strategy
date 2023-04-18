from pytest_mock import MockerFixture
from typing import Dict
from unittest.mock import MagicMock

from ltspipe.data.competitions import CompetitionInfo, ParserSettings
from ltspipe.messages import Message
from ltspipe.steps.api import ApiParserSettingsStep
from tests.conftest import mock_requests_get
from tests.mocks.logging import FakeLogger


class TestApiParserSettingsStep:
    """Test ltspipe.steps.bulk.ApiParserSettingsStep class."""

    API_LTS = 'http://localhost:8090/'

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
        step = ApiParserSettingsStep(
            logger=fake_logger,
            api_lts=self.API_LTS,
            competitions=in_competitions,
            next_step=next_step,
        )

        # Run step and validate that the competition info is retrieved
        step.run_step(sample_message)
        expected_competitions = {
            competition_code: CompetitionInfo(
                id=1,
                competition_code=competition_code,
                parser_settings={
                    ParserSettings.TIMING_NAME: 'sample-name',
                    ParserSettings.TIMING_RANKING: 'sample-ranking',
                },
            ),
        }
        assert in_competitions == expected_competitions

        assert next_step.run_step.call_count == 1
        received_msg: Message = next_step.run_step.call_args_list[0][0][0]
        assert received_msg.competition_code == competition_code
        assert received_msg.data == sample_message.data

        # Also, check that the get_children method returns the mocks
        children = step.get_children()
        assert children == [next_step]

    def _apply_mock_api(self, mocker: MockerFixture) -> None:
        """Apply mock to API."""
        first_response = {
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
        second_response = [
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
        responses: list = [first_response, second_response]
        _ = mock_requests_get(mocker, responses=responses)

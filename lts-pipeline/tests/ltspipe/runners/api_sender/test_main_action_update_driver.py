from datetime import datetime
import pytest
from pytest_mock import MockerFixture
import tempfile
from typing import Dict, List

from ltspipe.configs import (
    ApiSenderConfig,
    DEFAULT_NOTIFICATIONS_TOPIC,
    DEFAULT_STD_MESSAGES_TOPIC,
)
from ltspipe.data.actions import Action, ActionType
from ltspipe.data.auth import AuthRole
from ltspipe.data.competitions import (
    CompetitionInfo,
    Driver,
    Team,
    UpdateDriver,
)
from ltspipe.data.enum import ParserSettings
from ltspipe.data.notifications import Notification, NotificationType
from ltspipe.messages import Message, MessageDecoder, MessageSource
from ltspipe.runners.api_sender.main import main
from tests.conftest import (
    mock_kafka_consumer_builder,
    mock_kafka_producer_builder,
    mock_multiprocessing_dict,
    mock_requests,
)
from tests.fixtures import MOCK_API_LTS, MOCK_KAFKA, TEST_COMPETITION_CODE
from tests.mocks.logging import FakeLogger
from tests.mocks.multiprocessing import MockProcess
from tests.mocks.requests import (
    MapRequestItem,
    MapRequestMethod,
    MockResponse,
)

EXCLUDED_KEYS = {
    'created_at': True,
    'updated_at': True,
}
PARSERS_SETTINGS = {
    ParserSettings.TIMING_NAME: 'timing-name-value',
    ParserSettings.TIMING_RANKING: 'timing-ranking-value',
}


def _mock_multiprocessing_process(mocker: MockerFixture) -> None:
    """Mock parallel processes by sequential ones."""
    mocker.patch(
        'ltspipe.runners.api_sender.main._create_process',
        new=MockProcess)


@pytest.mark.parametrize(
    ('kafka_topics, in_competitions, expected_kafka, expected_competitions'),
    [
        (
            {  # kafka_topics
                DEFAULT_NOTIFICATIONS_TOPIC: [],
                DEFAULT_STD_MESSAGES_TOPIC: [
                    Message(
                        competition_code=TEST_COMPETITION_CODE,
                        data=Action(
                            type=ActionType.UPDATE_DRIVER,
                            data=UpdateDriver(
                                id=1,
                                competition_code=TEST_COMPETITION_CODE,
                                participant_code='r5625',
                                name='CKM 1 Driver 1',
                                number=51,
                                team_id=1,
                            ),
                        ),
                        source=MessageSource.SOURCE_WS_LISTENER,
                        decoder=MessageDecoder.ACTION,
                        created_at=datetime.utcnow().timestamp(),
                        updated_at=datetime.utcnow().timestamp(),
                    ).encode(),
                ],
            },
            {  # in_competitions
                TEST_COMPETITION_CODE: CompetitionInfo(
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings=PARSERS_SETTINGS,
                    drivers=[],
                    teams=[
                        Team(
                            id=1,
                            participant_code='r5625',
                            name='CKM 1',
                            number=41,
                        ),
                    ],
                    timing=[],
                ),
            },  # in_competitions
            {  # expected_kafka
                DEFAULT_NOTIFICATIONS_TOPIC: [
                    Message(
                        competition_code=TEST_COMPETITION_CODE,
                        data=Notification(
                            type=NotificationType.UPDATED_DRIVER,
                            data=Driver(
                                id=1,
                                participant_code='r5625',
                                name='CKM 1 Driver 1',
                                team_id=1,
                                number=51,
                                partial_driving_time=0,
                                total_driving_time=0,
                            ),
                        ),
                        source=MessageSource.SOURCE_WS_LISTENER,
                        created_at=datetime.utcnow().timestamp(),
                        updated_at=datetime.utcnow().timestamp(),
                        decoder=MessageDecoder.NOTIFICATION,
                    ).encode(),
                ],
                DEFAULT_STD_MESSAGES_TOPIC: [
                    Message(
                        competition_code=TEST_COMPETITION_CODE,
                        data=Action(
                            type=ActionType.UPDATE_DRIVER,
                            data=UpdateDriver(
                                id=1,
                                competition_code=TEST_COMPETITION_CODE,
                                participant_code='r5625',
                                name='CKM 1 Driver 1',
                                number=51,
                                team_id=1,
                            ),
                        ),
                        source=MessageSource.SOURCE_WS_LISTENER,
                        decoder=MessageDecoder.ACTION,
                        created_at=datetime.utcnow().timestamp(),
                        updated_at=datetime.utcnow().timestamp(),
                    ).encode(),
                ],
            },
            {  # expected_competitions
                TEST_COMPETITION_CODE: CompetitionInfo(
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings=PARSERS_SETTINGS,
                    drivers=[
                        Driver(
                            id=1,
                            participant_code='r5625',
                            name='CKM 1 Driver 1',
                            team_id=1,
                            number=51,
                            partial_driving_time=0,
                            total_driving_time=0,
                        ),
                    ],
                    teams=[
                        Team(
                            id=1,
                            participant_code='r5625',
                            name='CKM 1',
                            number=41,
                        ),
                    ],
                ),
            },
        ),
    ],
)
def test_main(
        mocker: MockerFixture,
        kafka_topics: Dict[str, List[str]],
        in_competitions: Dict[str, CompetitionInfo],
        expected_kafka: Dict[str, List[str]],
        expected_competitions: Dict[str, CompetitionInfo]) -> None:
    """
    Test main method.

    Test case: it receives an action to update a driver. After it sends the
    data to the API, it should generate a notification.
    """
    with tempfile.TemporaryDirectory() as tmp_path:
        config = ApiSenderConfig(
            api_lts=MOCK_API_LTS,
            errors_path=tmp_path,
            kafka_servers=MOCK_KAFKA,
        )

        _apply_mock_api(mocker, MOCK_API_LTS)
        _mock_multiprocessing_process(mocker)
        mock_multiprocessing_dict(mocker, initial_dicts=[in_competitions])
        mock_kafka_consumer_builder(mocker, kafka_topics=kafka_topics)
        mock_kafka_producer_builder(mocker, kafka_topics=kafka_topics)
        fake_logger = FakeLogger()

        main(config=config, logger=fake_logger)

        # Validate that the value of the flag is the expected one
        assert in_competitions == expected_competitions

        # Validate that the messages are received by Kafka
        out_kafka = {topic: _raw_to_dict(raw)
                    for topic, raw in kafka_topics.items()}
        assert (out_kafka == {topic: _raw_to_dict(raw)
                            for topic, raw in expected_kafka.items()})


def _raw_to_dict(raw: List[str]) -> List[dict]:
    """Transform messages into dictionaries."""
    return [Message.decode(x).dict(exclude=EXCLUDED_KEYS) for x in raw]


def _mock_response_auth_key(api_url: str) -> List[MapRequestItem]:
    """Get mocked response."""
    response = MockResponse(
        content={
            'bearer': 'sample-bearer-token',
            'role': AuthRole.BATCH.value,
            'name': 'Test',
        },
    )
    item = MapRequestItem(
        url=f'{api_url}/v1/auth',
        method=MapRequestMethod.POST,
        responses=[response],
    )
    return [item]


def _mock_response_delete_parser_settings(api_url: str) -> List[MapRequestItem]:
    """Get mocked response."""
    response = MockResponse(content={})
    item = MapRequestItem(
        url=f'{api_url}/v1/c/1/parsers/settings',
        method=MapRequestMethod.DELETE,
        responses=[response],
    )
    return [item]


def _mock_response_get_drivers(api_url: str) -> List[MapRequestItem]:
    """Get mocked response."""
    return [
        MapRequestItem(
            url=f'{api_url}/v1/c/1/drivers/1',
            method=MapRequestMethod.GET,
            responses=[
                MockResponse(content={
                    'id': 1,
                    'competition_id': 1,
                    'team_id': 1,
                    'participant_code': 'r5625',
                    'name': 'CKM 1 Driver 1',
                    'number': 41,
                    'total_driving_time': 0,
                    'partial_driving_time': 0,
                    'insert_date': '2023-04-20T20:42:51',
                    'update_date': '2023-04-20T20:42:51',
                }),
            ],
        ),
    ]


def _mock_response_get_team_driver_by_name(
        api_url: str) -> List[MapRequestItem]:
    """Get mocked response."""
    return [
        MapRequestItem(
            url=f'{api_url}/v1/c/1/teams/1/drivers/filter/name/CKM 1 Driver 1',
            method=MapRequestMethod.GET,
            responses=[
                MockResponse(content={}),
            ],
        ),
    ]


def _mock_response_post_drivers(api_url: str) -> List[MapRequestItem]:
    """Get mocked response."""
    return [
        MapRequestItem(
            url=f'{api_url}/v1/c/1/teams/1/drivers',
            method=MapRequestMethod.POST,
            responses=[
                MockResponse(
                    content={
                        'id': 1,
                        'competition_id': 1,
                        'team_id': 1,
                        'participant_code': 'r5625',
                        'name': 'CKM 1 Driver 1',
                        'number': 51,
                        'total_driving_time': 0,
                        'partial_driving_time': 0,
                        'insert_date': '2023-04-20T20:42:51',
                        'update_date': '2023-04-20T20:42:51',
                    },
                ),
            ],
        ),
    ]


def _apply_mock_api(mocker: MockerFixture, api_url: str) -> None:
    """Apply mock to API."""
    api_url = api_url.strip('/')
    requests_map = (
        _mock_response_auth_key(api_url)
        + _mock_response_delete_parser_settings(api_url)
        + _mock_response_get_drivers(api_url)
        + _mock_response_get_team_driver_by_name(api_url)
        + _mock_response_post_drivers(api_url))
    mock_requests(mocker, requests_map=requests_map)

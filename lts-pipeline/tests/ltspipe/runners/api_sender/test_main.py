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
from ltspipe.data.competitions import (
    CompetitionInfo,
    CompetitionStatus,
    CompetitionStage,
    DiffLap,
    Driver,
    InitialData,
    Participant,
    Team,
)
from ltspipe.data.enum import (
    LengthUnit,
    ParserSettings,
)
from ltspipe.messages import Message, MessageDecoder, MessageSource
from ltspipe.data.notifications import Notification, NotificationType
from ltspipe.runners.api_sender.main import main
from tests.conftest import (
    mock_kafka_consumer_builder,
    mock_kafka_producer_builder,
    mock_multiprocessing_dict,
    mock_requests,
    TEST_COMPETITION_CODE,
)
from tests.mocks.logging import FakeLogger
from tests.mocks.requests import (
    MapRequestItem,
    MapRequestMethod,
    MockResponse,
)

API_LTS = 'http://localhost:8090/'
EXCLUDED_KEYS = {
    'created_at': True,
    'updated_at': True,
}
KAFKA_SERVERS = ['localhost:9092']
PARSERS_SETTINGS = {
    ParserSettings.TIMING_NAME: 'timing-name-value',
    ParserSettings.TIMING_RANKING: 'timing-ranking-value',
}


@pytest.mark.parametrize(
    ('kafka_topics, in_competitions, expected_kafka, expected_competitions'),
    [
        # Test case: When the flag 'wait-init' is enabled and it receives an
        # initializer message, it parses the data anyway.
        (
            {  # kafka_topics
                DEFAULT_NOTIFICATIONS_TOPIC: [],
                DEFAULT_STD_MESSAGES_TOPIC: [
                    Message(
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
                                parsers_settings=PARSERS_SETTINGS,
                                participants={
                                    'r5625': Participant(
                                        participant_code='r5625',
                                        ranking=1,
                                        kart_number=41,
                                        team_name='CKM 1',
                                        driver_name='CKM 1 Driver 1',
                                    ),
                                    'r5626': Participant(
                                        participant_code='r5626',
                                        ranking=2,
                                        kart_number=42,
                                        team_name='CKM 2',
                                        driver_name='CKM 2 Driver 1',
                                    ),
                                    'r5627': Participant(
                                        participant_code='r5627',
                                        ranking=3,
                                        kart_number=43,
                                        team_name='CKM 3',
                                        driver_name='CKM 3 Driver 3',
                                    ),
                                },
                            ),
                        ),
                        source=MessageSource.SOURCE_WS_LISTENER,
                        decoder=MessageDecoder.ACTION,
                        created_at=datetime.utcnow().timestamp(),
                        updated_at=datetime.utcnow().timestamp(),
                    ).encode(),
                ],
            },
            {},  # in_competitions
            {  # expected_kafka
                DEFAULT_NOTIFICATIONS_TOPIC: [
                    Message(
                        competition_code=TEST_COMPETITION_CODE,
                        data=Notification(
                            type=NotificationType.INIT_FINISHED,
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
                            type=ActionType.INITIALIZE,
                            data=InitialData(
                                competition_code=TEST_COMPETITION_CODE,
                                stage=CompetitionStage.QUALIFYING.value,
                                status=CompetitionStatus.ONGOING.value,
                                remaining_length=DiffLap(
                                    value=1200000,
                                    unit=LengthUnit.MILLIS,
                                ),
                                parsers_settings=PARSERS_SETTINGS,
                                participants={
                                    'r5625': Participant(
                                        participant_code='r5625',
                                        ranking=1,
                                        kart_number=41,
                                        team_name='CKM 1',
                                        driver_name='CKM 1 Driver 1',
                                    ),
                                    'r5626': Participant(
                                        participant_code='r5626',
                                        ranking=2,
                                        kart_number=42,
                                        team_name='CKM 2',
                                        driver_name='CKM 2 Driver 1',
                                    ),
                                    'r5627': Participant(
                                        participant_code='r5627',
                                        ranking=3,
                                        kart_number=43,
                                        team_name='CKM 3',
                                        driver_name='CKM 3 Driver 3',
                                    ),
                                },
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
                        ),
                        Driver(
                            id=2,
                            participant_code='r5626',
                            name='CKM 2 Driver 1',
                            team_id=2,
                        ),
                        Driver(
                            id=3,
                            participant_code='r5627',
                            name='CKM 3 Driver 3',
                            team_id=3,
                        ),
                    ],
                    teams=[
                        Team(
                            id=1,
                            participant_code='r5625',
                            name='CKM 1',
                        ),
                        Team(
                            id=2,
                            participant_code='r5626',
                            name='CKM 2',
                        ),
                        Team(
                            id=3,
                            participant_code='r5627',
                            name='CKM 3',
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
    """Test main method."""
    with tempfile.TemporaryDirectory() as tmp_path:
        config = ApiSenderConfig(
            api_lts=API_LTS,
            errors_path=tmp_path,
            kafka_servers=KAFKA_SERVERS,
        )

        _apply_mock_api(mocker, API_LTS)
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


def _mock_response_delete_parser_settings(api_url: str) -> List[MapRequestItem]:
    """Get mocked response."""
    response = MockResponse(content={})
    item = MapRequestItem(
        url=f'{api_url}/v1/competitions/1/parsers/settings',
        method=MapRequestMethod.DELETE,
        responses=[response],
    )
    return [item]


def _mock_response_get_competition_info(api_url: str) -> List[MapRequestItem]:
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
            'name': 'Sample competition',
            'description': 'Endurance in Karting North',
            'insert_date': '2023-04-15T21:43:26',
            'update_date': '2023-04-15T21:43:26',
        },
    )
    item = MapRequestItem(
        url=f'{api_url}/v1/competitions/filter/code/{TEST_COMPETITION_CODE}',
        method=MapRequestMethod.GET,
        responses=[response],
    )
    return [item]


def _mock_response_get_competition_metadata(
        api_url: str) -> List[MapRequestItem]:
    """Get mocked response."""
    responses = [
        MockResponse(
            content={
                'reference_time': 0,
                'reference_current_offset': 0,
                'status': 'ongoing',
                'stage': 'qualifying',
                'remaining_length': 350,
                'remaining_length_unit': 'laps',
                'insert_date': '2023-04-20T20:42:51',
                'update_date': '2023-04-20T21:59:45',
            },
        ),
    ]
    item = MapRequestItem(
        url=f'{api_url}/v1/competitions/1/metadata',
        method=MapRequestMethod.GET,
        responses=responses,
    )
    return [item]


def _mock_response_get_parser_settings(api_url: str) -> List[MapRequestItem]:
    """Get mocked response."""
    response = MockResponse(
        content=[
            {
                'name': ParserSettings.TIMING_NAME,
                'value': 'timing-name-value',
                'insert_date': '2023-04-15T21:43:26',
                'update_date': '2023-04-15T21:43:26',
            },
            {
                'name': ParserSettings.TIMING_RANKING,
                'value': 'timing-ranking-value',
                'insert_date': '2023-04-15T21:43:26',
                'update_date': '2023-04-15T21:43:26',
            },
        ],
    )
    item = MapRequestItem(
        url=f'{api_url}/v1/competitions/1/parsers/settings',
        method=MapRequestMethod.GET,
        responses=[response],
    )
    return [item]


def _mock_response_get_drivers(api_url: str) -> List[MapRequestItem]:
    """Get mocked response."""
    response = MockResponse(content=[])
    item = MapRequestItem(
        url=f'{api_url}/v1/competitions/1/drivers',
        method=MapRequestMethod.GET,
        responses=[response],
    )
    return [item]


def _mock_response_get_teams(api_url: str) -> List[MapRequestItem]:
    """Get mocked response."""
    response = MockResponse(content=[])
    item = MapRequestItem(
        url=f'{api_url}/v1/competitions/1/teams',
        method=MapRequestMethod.GET,
        responses=[response],
    )
    return [item]


def _mock_response_post_drivers(api_url: str) -> List[MapRequestItem]:
    """Get mocked response."""
    return [
        MapRequestItem(
            url=f'{api_url}/v1/competitions/1/teams/1/drivers',
            method=MapRequestMethod.POST,
            responses=[
                MockResponse(
                    content={
                        'id': 1,
                        'competition_id': 1,
                        'team_id': 1,
                        'participant_code': 'r5625',
                        'name': 'CKM 1 Driver 1',
                        'number': 41,
                        'total_driving_time': 0,
                        'partial_driving_time': 0,
                        'reference_time_offset': 0,
                        'insert_date': '2023-04-20T20:42:51',
                        'update_date': '2023-04-20T20:42:51',
                    },
                ),
            ],
        ),
        MapRequestItem(
            url=f'{api_url}/v1/competitions/1/teams/2/drivers',
            method=MapRequestMethod.POST,
            responses=[
                MockResponse(
                    content={
                        'id': 2,
                        'competition_id': 1,
                        'team_id': 2,
                        'participant_code': 'r5626',
                        'name': 'CKM 2 Driver 1',
                        'number': 42,
                        'total_driving_time': 0,
                        'partial_driving_time': 0,
                        'reference_time_offset': 0,
                        'insert_date': '2023-04-20T20:42:51',
                        'update_date': '2023-04-20T20:42:51',
                    },
                ),
            ],
        ),
        MapRequestItem(
            url=f'{api_url}/v1/competitions/1/teams/3/drivers',
            method=MapRequestMethod.POST,
            responses=[
                MockResponse(
                    content={
                        'id': 3,
                        'competition_id': 1,
                        'team_id': 3,
                        'participant_code': 'r5627',
                        'name': 'CKM 3 Driver 1',
                        'number': 43,
                        'total_driving_time': 0,
                        'partial_driving_time': 0,
                        'reference_time_offset': 0,
                        'insert_date': '2023-04-20T20:42:51',
                        'update_date': '2023-04-20T20:42:51',
                    },
                ),
            ],
        ),
    ]


def _mock_response_post_parsers_settings(api_url: str) -> List[MapRequestItem]:
    """Get mocked response."""
    return [
        MapRequestItem(
            url=f'{api_url}/v1/competitions/1/parsers/settings',
            method=MapRequestMethod.POST,
            responses=[
                MockResponse(
                    content={
                        'name': 'timing-name',
                        'value': 'timing-name-value',
                    },
                ),
                MockResponse(
                    content={
                        'name': 'timing-ranking',
                        'value': 'timing-ranking-value',
                    },
                ),
            ],
        ),
    ]


def _mock_response_post_teams(api_url: str) -> List[MapRequestItem]:
    """Get mocked response."""
    responses = [
        MockResponse(
            content={
                'id': 1,
                'competition_id': 1,
                'participant_code': 'r5625',
                'name': 'CKM 1',
                'number': 41,
                'reference_time_offset': 0,
                'drivers': [],
                'insert_date': '2023-04-20T20:42:51',
                'update_date': '2023-04-20T20:42:51',
            },
        ),
        MockResponse(
            content={
                'id': 2,
                'competition_id': 1,
                'participant_code': 'r5626',
                'name': 'CKM 2',
                'number': 42,
                'reference_time_offset': 0,
                'drivers': [],
                'insert_date': '2023-04-20T20:42:51',
                'update_date': '2023-04-20T20:42:51',
            },
        ),
        MockResponse(
            content={
                'id': 3,
                'competition_id': 1,
                'participant_code': 'r5627',
                'name': 'CKM 3',
                'number': 43,
                'reference_time_offset': 0,
                'drivers': [],
                'insert_date': '2023-04-20T20:42:51',
                'update_date': '2023-04-20T20:42:51',
            },
        ),
    ]
    item = MapRequestItem(
        url=f'{api_url}/v1/competitions/1/teams',
        method=MapRequestMethod.POST,
        responses=responses,
    )
    return [item]


def _mock_response_update_competition_metadata(
        api_url: str) -> List[MapRequestItem]:
    """Get mocked response."""
    responses = [
        MockResponse(
            content={
                'reference_time': 0,
                'reference_current_offset': 0,
                'status': 'ongoing',
                'stage': 'race',
                'remaining_length': 350,
                'remaining_length_unit': 'laps',
                'insert_date': '2023-04-20T20:42:51',
                'update_date': '2023-04-20T21:59:45',
            },
        ),
    ]
    item = MapRequestItem(
        url=f'{api_url}/v1/competitions/1/metadata',
        method=MapRequestMethod.PUT,
        responses=responses,
    )
    return [item]


def _mock_response_update_timing(api_url: str) -> List[MapRequestItem]:
    """Get mocked response."""
    return [
        MapRequestItem(
            url=f'{api_url}/v1/competitions/1/timing/team/1',
            method=MapRequestMethod.PUT,
            responses=[
                MockResponse(
                    content={
                        'team_id': 1,
                        'driver_id': 1,
                        'position': 1,
                        'time': 58800,
                        'best_time': 58800,
                        'lap': 5,
                        'interval': 0,
                        'interval_unit': 'millis',
                        'stage': 'race',
                        'pits': 0,
                        'kart_status': 'good',
                        'fixed_kart_status': None,
                        'number_pits': 0,
                        'insert_date': '2023-04-20T20:42:51',
                        'update_date': '2023-04-20T22:27:33',
                    },
                ),
            ],
        ),
        MapRequestItem(
            url=f'{api_url}/v1/competitions/1/timing/team/2',
            method=MapRequestMethod.PUT,
            responses=[
                MockResponse(
                    content={
                        'team_id': 2,
                        'driver_id': 2,
                        'position': 2,
                        'time': 58800,
                        'best_time': 58800,
                        'lap': 5,
                        'interval': 0,
                        'interval_unit': 'millis',
                        'stage': 'race',
                        'pits': 0,
                        'kart_status': 'good',
                        'fixed_kart_status': None,
                        'number_pits': 0,
                        'insert_date': '2023-04-20T20:42:51',
                        'update_date': '2023-04-20T22:27:33',
                    },
                ),
            ],
        ),
        MapRequestItem(
            url=f'{api_url}/v1/competitions/1/timing/team/3',
            method=MapRequestMethod.PUT,
            responses=[
                MockResponse(
                    content={
                        'team_id': 3,
                        'driver_id': 3,
                        'position': 3,
                        'time': 58800,
                        'best_time': 58800,
                        'lap': 5,
                        'interval': 0,
                        'interval_unit': 'millis',
                        'stage': 'race',
                        'pits': 0,
                        'kart_status': 'good',
                        'fixed_kart_status': None,
                        'number_pits': 0,
                        'insert_date': '2023-04-20T20:42:51',
                        'update_date': '2023-04-20T22:27:33',
                    },
                ),
            ],
        ),
    ]


def _apply_mock_api(mocker: MockerFixture, api_url: str) -> None:
    """Apply mock to API."""
    api_url = api_url.strip('/')
    requests_map = (
        _mock_response_delete_parser_settings(api_url)
        + _mock_response_get_competition_info(api_url)
        + _mock_response_get_competition_metadata(api_url)
        + _mock_response_get_drivers(api_url)
        + _mock_response_get_parser_settings(api_url)
        + _mock_response_get_teams(api_url)
        + _mock_response_post_drivers(api_url)
        + _mock_response_post_parsers_settings(api_url)
        + _mock_response_post_teams(api_url)
        + _mock_response_update_competition_metadata(api_url)
        + _mock_response_update_timing(api_url))
    mock_requests(mocker, requests_map=requests_map)

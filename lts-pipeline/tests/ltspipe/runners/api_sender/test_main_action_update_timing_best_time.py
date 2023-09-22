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
    CompetitionStage,
    DiffLap,
    KartStatus,
    LengthUnit,
    Team,
    ParticipantTiming,
    UpdateTimingBestTime,
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
    ParserSettings.TIMING_BEST_TIME: 'timing-best-time-value',
}


def _mock_multiprocessing_process(mocker: MockerFixture) -> None:
    """Mock parallel processes by sequential ones."""
    mocker.patch(
        'ltspipe.runners.api_sender.main._create_process',
        new=MockProcess)


@pytest.mark.parametrize(
    'kafka_topics, in_competitions, expected_kafka',
    [
        (
            {  # kafka_topics
                DEFAULT_NOTIFICATIONS_TOPIC: [],
                DEFAULT_STD_MESSAGES_TOPIC: [
                    Message(
                        competition_code=TEST_COMPETITION_CODE,
                        data=Action(
                            type=ActionType.UPDATE_TIMING_BEST_TIME,
                            data=UpdateTimingBestTime(
                                competition_code=TEST_COMPETITION_CODE,
                                team_id=1,
                                best_time=52000,
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
                    timing={},
                ),
            },
            {  # expected_kafka
                DEFAULT_NOTIFICATIONS_TOPIC: [
                    Message(
                        competition_code=TEST_COMPETITION_CODE,
                        data=Notification(
                            type=NotificationType.UPDATED_TIMING_BEST_TIME,
                            data=ParticipantTiming(
                                best_time=52000,
                                driver_id=1,
                                fixed_kart_status=None,
                                gap=None,
                                interval=DiffLap(
                                    value=0, unit=LengthUnit.MILLIS),
                                kart_status=KartStatus.GOOD,
                                lap=6,
                                last_time=65000,
                                number_pits=0,
                                participant_code='team-1',
                                pit_time=0,
                                position=1,
                                stage=CompetitionStage.RACE,
                                team_id=1,
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
                            type=ActionType.UPDATE_TIMING_BEST_TIME,
                            data=UpdateTimingBestTime(
                                competition_code=TEST_COMPETITION_CODE,
                                team_id=1,
                                best_time=52000,
                            ),
                        ),
                        source=MessageSource.SOURCE_WS_LISTENER,
                        decoder=MessageDecoder.ACTION,
                        created_at=datetime.utcnow().timestamp(),
                        updated_at=datetime.utcnow().timestamp(),
                    ).encode(),
                ],
            },
        ),
    ],
)
def test_main(
        mocker: MockerFixture,
        kafka_topics: Dict[str, List[str]],
        in_competitions: Dict[str, CompetitionInfo],
        expected_kafka: Dict[str, List[str]]) -> None:
    """
    Test main method.

    Test case: it receives an action to update the timing. After it sends the
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

        # Validate that the messages are received by Kafka
        out_kafka = {topic: _raw_to_dict(raw)
                    for topic, raw in kafka_topics.items()}
        assert (out_kafka == {topic: _raw_to_dict(raw)
                            for topic, raw in expected_kafka.items()})


def _raw_to_dict(raw: List[str]) -> List[dict]:
    """Transform messages into dictionaries."""
    return [Message.decode(x).model_dump(exclude=EXCLUDED_KEYS) for x in raw]


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


def _mock_response_put_timing_best_time(api_url: str) -> List[MapRequestItem]:
    """Get mocked response."""
    return [
        MapRequestItem(
            url=f'{api_url}/v1/c/1/timing/teams/1/best_time',
            method=MapRequestMethod.PUT,
            responses=[
                MockResponse(
                    content={
                        'best_time': 52000,
                        'driver_id': 1,
                        'fixed_kart_status': None,
                        'gap': None,
                        'gap_unit': 'millis',
                        'interval': 0,
                        'interval_unit': 'millis',
                        'kart_status': 'good',
                        'lap': 6,
                        'last_time': 65000,
                        'number_pits': 0,
                        'participant_code': 'team-1',
                        'pit_time': 0,
                        'position': 1,
                        'stage': 'race',
                        'team_id': 1,
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
        _mock_response_auth_key(api_url)
        + _mock_response_put_timing_best_time(api_url))
    mock_requests(mocker, requests_map=requests_map)
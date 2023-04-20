from datetime import datetime
import pytest
from pytest_mock import MockerFixture
import tempfile
from typing import Any, Dict, List

from ltspipe.data.actions import Action, ActionType
from ltspipe.data.competitions import (
    CompetitionStatus,
    CompetitionStage,
    DiffLap,
    InitialData,
    Participant,
)
from ltspipe.data.enum import (
    FlagName,
    LengthUnit,
    ParserSettings,
)
from ltspipe.configs import (
    ParserConfig,
    DEFAULT_NOTIFICATIONS_TOPIC,
    DEFAULT_RAW_MESSAGES_TOPIC,
    DEFAULT_STD_MESSAGES_TOPIC,
)
from ltspipe.messages import Message, MessageDecoder, MessageSource
from tests.mocks.requests import (
    MapRequestItem,
    MapRequestMethod,
    MockResponse,
)
from ltspipe.runners.parser.main import main
from tests.conftest import (
    mock_kafka_consumer_builder,
    mock_kafka_producer_builder,
    mock_multiprocessing_dict,
    mock_requests,
    TEST_COMPETITION_CODE,
)
from tests.helpers import load_raw_message
from tests.mocks.logging import FakeLogger

API_LTS = 'http://localhost:8090/'
EXCLUDED_KEYS = {
    'created_at': True,
    'updated_at': True,
}
KAFKA_SERVERS = ['localhost:9092']
PARSERS_SETTINGS = {
    ParserSettings.TIMING_RANKING: 'c3',
    ParserSettings.TIMING_KART_NUMBER: 'c4',
    ParserSettings.TIMING_NAME: 'c5',
    ParserSettings.TIMING_LAST_LAP_TIME: 'c6',
    ParserSettings.TIMING_BEST_TIME: 'c7',
    ParserSettings.TIMING_GAP: 'c8',
    ParserSettings.TIMING_INTERVAL: 'c9',
    ParserSettings.TIMING_PIT_TIME: 'c10',
    ParserSettings.TIMING_PITS: 'c11',
}


@pytest.mark.parametrize(
    ('kafka_topics, in_flags, in_queue,'
     'expected_kafka, expected_queue, expected_flags'),
    [
        # Test case: When the flag 'wait-init' is enabled and it receives an
        # initializer message, it parses the data anyway.
        (
            {  # kafka_topics
                DEFAULT_NOTIFICATIONS_TOPIC: [],
                DEFAULT_RAW_MESSAGES_TOPIC: [
                    Message(
                        competition_code=TEST_COMPETITION_CODE,
                        data=load_raw_message(
                            'initial_3_teams_with_times.txt').strip(),
                        source=MessageSource.SOURCE_WS_LISTENER,
                        created_at=datetime.utcnow().timestamp(),
                        updated_at=datetime.utcnow().timestamp(),
                        error_description=None,
                        error_traceback=None,
                    ).encode(),
                ],
                DEFAULT_STD_MESSAGES_TOPIC: [],
            },
            {TEST_COMPETITION_CODE: {FlagName.WAIT_INIT: True}},  # in_flags
            {},  # in_queue
            {  # expected_kafka
                DEFAULT_NOTIFICATIONS_TOPIC: [],
                DEFAULT_RAW_MESSAGES_TOPIC: [
                    Message(
                        competition_code=TEST_COMPETITION_CODE,
                        data=load_raw_message(
                            'initial_3_teams_with_times.txt').strip(),
                        source=MessageSource.SOURCE_WS_LISTENER,
                        created_at=datetime.utcnow().timestamp(),
                        updated_at=datetime.utcnow().timestamp(),
                        error_description=None,
                        error_traceback=None,
                    ).encode(),
                ],
                DEFAULT_STD_MESSAGES_TOPIC: [
                    Message(
                        competition_code=TEST_COMPETITION_CODE,
                        data=Action(
                            type=ActionType.INITIALIZE,
                            data=InitialData(
                                competition_code=TEST_COMPETITION_CODE,
                                reference_time=None,
                                reference_current_offset=None,
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
                                        kart_number=1,
                                        team_name='CKM 1',
                                        last_lap_time=65142,  # 1:05.142
                                        best_time=64882,  # 1:04.882
                                    ),
                                    'r5626': Participant(
                                        participant_code='r5626',
                                        ranking=2,
                                        kart_number=2,
                                        team_name='CKM 2',
                                        last_lap_time=65460,  # 1:05.460
                                        best_time=64890,  # 1:04.890
                                        pits=1,
                                    ),
                                    'r5627': Participant(
                                        participant_code='r5627',
                                        ranking=3,
                                        kart_number=3,
                                        team_name='CKM 3',
                                        last_lap_time=65411,  # 1:05.411
                                        best_time=64941,  # 1:04.941
                                        gap=DiffLap(
                                            value=1,  # 1 lap
                                            unit=LengthUnit.LAPS.value,
                                        ),
                                        interval=DiffLap(
                                            value=12293,  # 12.293
                                            unit=LengthUnit.MILLIS.value,
                                        ),
                                        pits=2,
                                        pit_time=54000,  # 54.
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
            {},  # expected_queue
            {  # expected_flags
                TEST_COMPETITION_CODE: {FlagName.WAIT_INIT: True},
            },
        ),
        # Test case: When the flag 'wait-init' is enabled and it receives a
        # new message, it ends up in the queue.
        (
            {  # kafka_topics
                DEFAULT_NOTIFICATIONS_TOPIC: [],
                DEFAULT_RAW_MESSAGES_TOPIC: [
                    Message(
                        competition_code=TEST_COMPETITION_CODE,
                        data=load_raw_message(
                            'display_driver_name.txt').strip(),
                        source=MessageSource.SOURCE_WS_LISTENER,
                        created_at=datetime.utcnow().timestamp(),
                        updated_at=datetime.utcnow().timestamp(),
                        error_description=None,
                        error_traceback=None,
                    ).encode(),
                ],
                DEFAULT_STD_MESSAGES_TOPIC: [],
            },
            {TEST_COMPETITION_CODE: {FlagName.WAIT_INIT: True}},  # in_flags
            {},  # in_queue
            {  # expected_kafka
                DEFAULT_NOTIFICATIONS_TOPIC: [],
                DEFAULT_RAW_MESSAGES_TOPIC: [
                    Message(
                        competition_code=TEST_COMPETITION_CODE,
                        data=load_raw_message(
                            'display_driver_name.txt').strip(),
                        source=MessageSource.SOURCE_WS_LISTENER,
                        created_at=datetime.utcnow().timestamp(),
                        updated_at=datetime.utcnow().timestamp(),
                        error_description=None,
                        error_traceback=None,
                    ).encode(),
                ],
                DEFAULT_STD_MESSAGES_TOPIC: [],
            },
            {  # expected_queue
                TEST_COMPETITION_CODE: [
                    Message(
                        competition_code=TEST_COMPETITION_CODE,
                        data=load_raw_message(
                            'display_driver_name.txt').strip(),
                        source=MessageSource.SOURCE_WS_LISTENER,
                        created_at=datetime.utcnow().timestamp(),
                        updated_at=datetime.utcnow().timestamp(),
                        error_description=None,
                        error_traceback=None,
                    ),
                ],
            },
            {  # expected_flags
                TEST_COMPETITION_CODE: {FlagName.WAIT_INIT: True},
            },
        ),
    ],
)
def test_main(
        mocker: MockerFixture,
        kafka_topics: Dict[str, List[str]],
        in_flags: Dict[str, Dict[FlagName, Any]],
        in_queue: Dict[str, List[Message]],
        expected_kafka: Dict[str, List[str]],
        expected_queue: Dict[str, List[Message]],
        expected_flags: dict) -> None:
    """Test main method."""
    with tempfile.TemporaryDirectory() as tmp_path:
        config = ParserConfig(
            api_lts=API_LTS,
            errors_path=tmp_path,
            kafka_servers=KAFKA_SERVERS,
            unknowns_path=tmp_path,
        )

        _apply_mock_api(mocker, API_LTS)
        mock_multiprocessing_dict(mocker, initial_dicts=[in_flags, in_queue])
        mock_kafka_consumer_builder(mocker, kafka_topics=kafka_topics)
        mock_kafka_producer_builder(mocker, kafka_topics=kafka_topics)
        fake_logger = FakeLogger()

        main(config=config, logger=fake_logger)

        # Validate that the value of the flag is the expected one
        assert in_flags == expected_flags

        # Validate that the messages are received by Kafka
        out_kafka = {topic: _raw_to_dict(raw)
                    for topic, raw in kafka_topics.items()}
        assert (out_kafka == {topic: _raw_to_dict(raw)
                            for topic, raw in expected_kafka.items()})

        # Validate that the expected messages are in the queue
        assert ({code: _msg_to_dict(x) for code, x in in_queue.items()}
                == {code: _msg_to_dict(x)
                    for code, x in expected_queue.items()})


def _raw_to_dict(raw: List[str]) -> List[dict]:
    """Transform messages into dictionaries."""
    return [Message.decode(x).dict(exclude=EXCLUDED_KEYS) for x in raw]


def _msg_to_dict(raw: List[Message]) -> List[dict]:
    """Transform messages into dictionaries."""
    return [x.dict(exclude=EXCLUDED_KEYS) for x in raw]


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


def _mock_response_get_parser_settings(api_url: str) -> List[MapRequestItem]:
    """Get mocked response."""
    response = MockResponse(
        content=[
            {
                'name': ParserSettings.TIMING_NAME.value,
                'value': 'timing-name-value',
                'insert_date': '2023-04-15T21:43:26',
                'update_date': '2023-04-15T21:43:26',
            },
            {
                'name': ParserSettings.TIMING_RANKING.value,
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


def _apply_mock_api(mocker: MockerFixture, api_url: str) -> None:
    """Apply mock to API."""
    api_url = api_url.strip('/')
    requests_map = (
        _mock_response_get_competition_info(api_url)
        + _mock_response_get_parser_settings(api_url))
    mock_requests(mocker, requests_map=requests_map)

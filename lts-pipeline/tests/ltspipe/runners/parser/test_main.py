from datetime import datetime
import pytest
from pytest_mock import MockerFixture
import tempfile
from typing import Any, Dict, List

from ltspipe.data.actions import Action, ActionType
from ltspipe.data.auth import AuthRole
from ltspipe.data.competitions import (
    AddPitIn,
    AddPitOut,
    CompetitionInfo,
    CompetitionStatus,
    CompetitionStage,
    DiffLap,
    InitialData,
    KartStatus,
    Participant,
    Team,
    UpdateCompetitionMetadataRemaining,
    UpdateCompetitionMetadataStatus,
    UpdateDriver,
    UpdateTeam,
    UpdateTimingPosition,
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
)
from tests.fixtures import MOCK_API_LTS, MOCK_KAFKA, TEST_COMPETITION_CODE
from tests.helpers import load_raw_message
from tests.mocks.logging import FakeLogger
from tests.mocks.multiprocessing import MockProcess

EXCLUDED_KEYS = {
    'created_at': True,
    'updated_at': True,
}
PARSERS_SETTINGS = {
    ParserSettings.TIMING_POSITION: 'c3',
    ParserSettings.TIMING_KART_NUMBER: 'c4',
    ParserSettings.TIMING_NAME: 'c5',
    ParserSettings.TIMING_LAST_LAP_TIME: 'c6',
    ParserSettings.TIMING_BEST_TIME: 'c7',
    ParserSettings.TIMING_GAP: 'c8',
    ParserSettings.TIMING_INTERVAL: 'c9',
    ParserSettings.TIMING_PIT_TIME: 'c10',
    ParserSettings.TIMING_NUMBER_PITS: 'c11',
}


def _mock_multiprocessing_process(mocker: MockerFixture) -> None:
    """Mock parallel processes by sequential ones."""
    mocker.patch(
        'ltspipe.runners.parser.main._create_process',
        new=MockProcess)


@pytest.mark.parametrize(
    ('kafka_topics, in_competitions, in_flags, in_queue,'
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
                            'init_qualy_with_times.txt').strip(),
                        source=MessageSource.SOURCE_WS_LISTENER,
                        created_at=datetime.utcnow().timestamp(),
                        updated_at=datetime.utcnow().timestamp(),
                        error_description=None,
                        error_traceback=None,
                    ).encode(),
                ],
                DEFAULT_STD_MESSAGES_TOPIC: [],
            },
            {},  # in_competitions
            {TEST_COMPETITION_CODE: {FlagName.WAIT_INIT: True}},  # in_flags
            {},  # in_queue
            {  # expected_kafka
                DEFAULT_NOTIFICATIONS_TOPIC: [],
                DEFAULT_RAW_MESSAGES_TOPIC: [
                    Message(
                        competition_code=TEST_COMPETITION_CODE,
                        data=load_raw_message(
                            'init_qualy_with_times.txt').strip(),
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
                                stage=CompetitionStage.QUALIFYING.value,
                                status=CompetitionStatus.PAUSED.value,
                                remaining_length=DiffLap(
                                    value=1200000,
                                    unit=LengthUnit.MILLIS,
                                ),
                                parsers_settings=PARSERS_SETTINGS,
                                participants={
                                    'r5625': Participant(
                                        best_time=64882,  # 1:04.882
                                        gap=DiffLap(
                                            value=0, unit=LengthUnit.MILLIS),
                                        interval=DiffLap(
                                            value=0, unit=LengthUnit.MILLIS),
                                        kart_number=1,
                                        laps=0,
                                        last_lap_time=65142,  # 1:05.142
                                        number_pits=0,
                                        participant_code='r5625',
                                        position=1,
                                        team_name='CKM 1',
                                    ),
                                    'r5626': Participant(
                                        best_time=64890,  # 1:04.890
                                        gap=DiffLap(
                                            value=0, unit=LengthUnit.MILLIS),
                                        interval=DiffLap(
                                            value=0, unit=LengthUnit.MILLIS),
                                        kart_number=2,
                                        laps=0,
                                        last_lap_time=65460,  # 1:05.460
                                        number_pits=1,
                                        participant_code='r5626',
                                        position=2,
                                        team_name='CKM 2',
                                    ),
                                    'r5627': Participant(
                                        best_time=64941,  # 1:04.941
                                        gap=DiffLap(
                                            value=1,  # 1 lap
                                            unit=LengthUnit.LAPS.value,
                                        ),
                                        interval=DiffLap(
                                            value=12293,  # 12.293
                                            unit=LengthUnit.MILLIS.value,
                                        ),
                                        kart_number=3,
                                        laps=0,
                                        last_lap_time=65411,  # 1:05.411
                                        number_pits=2,
                                        participant_code='r5627',
                                        pit_time=54000,  # 54.
                                        position=3,
                                        team_name='CKM 3',
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
                            'endurance_display_driver_name.txt').strip(),
                        source=MessageSource.SOURCE_WS_LISTENER,
                        created_at=datetime.utcnow().timestamp(),
                        updated_at=datetime.utcnow().timestamp(),
                        error_description=None,
                        error_traceback=None,
                    ).encode(),
                ],
                DEFAULT_STD_MESSAGES_TOPIC: [],
            },
            {},  # in_competitions
            {TEST_COMPETITION_CODE: {FlagName.WAIT_INIT: True}},  # in_flags
            {},  # in_queue
            {  # expected_kafka
                DEFAULT_NOTIFICATIONS_TOPIC: [],
                DEFAULT_RAW_MESSAGES_TOPIC: [
                    Message(
                        competition_code=TEST_COMPETITION_CODE,
                        data=load_raw_message(
                            'endurance_display_driver_name.txt').strip(),
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
                            'endurance_display_driver_name.txt').strip(),
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
        # Test case: When the flag 'wait-init' is disabled and it receives a
        # new message with a driver name.
        (
            {  # kafka_topics
                DEFAULT_NOTIFICATIONS_TOPIC: [],
                DEFAULT_RAW_MESSAGES_TOPIC: [
                    Message(
                        competition_code=TEST_COMPETITION_CODE,
                        data=load_raw_message(
                            'endurance_display_driver_name.txt').strip(),
                        source=MessageSource.SOURCE_WS_LISTENER,
                        created_at=datetime.utcnow().timestamp(),
                        updated_at=datetime.utcnow().timestamp(),
                        error_description=None,
                        error_traceback=None,
                    ).encode(),
                ],
                DEFAULT_STD_MESSAGES_TOPIC: [],
            },
            {},  # in_competitions
            {TEST_COMPETITION_CODE: {FlagName.WAIT_INIT: False}},  # in_flags
            {},  # in_queue
            {  # expected_kafka
                DEFAULT_NOTIFICATIONS_TOPIC: [],
                DEFAULT_RAW_MESSAGES_TOPIC: [
                    Message(
                        competition_code=TEST_COMPETITION_CODE,
                        data=load_raw_message(
                            'endurance_display_driver_name.txt').strip(),
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
                            type=ActionType.UPDATE_DRIVER,
                            data=UpdateDriver(
                                id=2,
                                competition_code=TEST_COMPETITION_CODE,
                                participant_code='r5625',
                                name='DIMAS MUNOZ',
                                number=41,
                                team_id=1,
                            ),
                        ),
                        source=MessageSource.SOURCE_WS_LISTENER,
                        decoder=MessageDecoder.ACTION,
                        created_at=datetime.utcnow().timestamp(),
                        updated_at=datetime.utcnow().timestamp(),
                        error_description=None,
                        error_traceback=None,
                    ).encode(),
                ],
            },
            {},  # expected_queue
            {  # expected_flags
                TEST_COMPETITION_CODE: {FlagName.WAIT_INIT: False},
            },
        ),
        # Test case: When the flag 'wait-init' is disabled and it receives a
        # new message with a team name.
        (
            {  # kafka_topics
                DEFAULT_NOTIFICATIONS_TOPIC: [],
                DEFAULT_RAW_MESSAGES_TOPIC: [
                    Message(
                        competition_code=TEST_COMPETITION_CODE,
                        data=load_raw_message(
                            'endurance_display_team_name.txt').strip(),
                        source=MessageSource.SOURCE_WS_LISTENER,
                        created_at=datetime.utcnow().timestamp(),
                        updated_at=datetime.utcnow().timestamp(),
                        error_description=None,
                        error_traceback=None,
                    ).encode(),
                ],
                DEFAULT_STD_MESSAGES_TOPIC: [],
            },
            {},  # in_competitions
            {TEST_COMPETITION_CODE: {FlagName.WAIT_INIT: False}},  # in_flags
            {},  # in_queue
            {  # expected_kafka
                DEFAULT_NOTIFICATIONS_TOPIC: [],
                DEFAULT_RAW_MESSAGES_TOPIC: [
                    Message(
                        competition_code=TEST_COMPETITION_CODE,
                        data=load_raw_message(
                            'endurance_display_team_name.txt').strip(),
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
                            type=ActionType.UPDATE_TEAM,
                            data=UpdateTeam(
                                id=1,
                                competition_code=TEST_COMPETITION_CODE,
                                participant_code='r5625',
                                name='CKM 1',
                                number=41,
                            ),
                        ),
                        source=MessageSource.SOURCE_WS_LISTENER,
                        decoder=MessageDecoder.ACTION,
                        created_at=datetime.utcnow().timestamp(),
                        updated_at=datetime.utcnow().timestamp(),
                        error_description=None,
                        error_traceback=None,
                    ).encode(),
                ],
            },
            {},  # expected_queue
            {  # expected_flags
                TEST_COMPETITION_CODE: {FlagName.WAIT_INIT: False},
            },
        ),
        # Test case: When the flag 'wait-init' is disabled and it receives a
        # new message with the competition status.
        (
            {  # kafka_topics
                DEFAULT_NOTIFICATIONS_TOPIC: [],
                DEFAULT_RAW_MESSAGES_TOPIC: [
                    Message(
                        competition_code=TEST_COMPETITION_CODE,
                        data=load_raw_message(
                            'endurance_status_finished.txt').strip(),
                        source=MessageSource.SOURCE_WS_LISTENER,
                        created_at=datetime.utcnow().timestamp(),
                        updated_at=datetime.utcnow().timestamp(),
                        error_description=None,
                        error_traceback=None,
                    ).encode(),
                ],
                DEFAULT_STD_MESSAGES_TOPIC: [],
            },
            {},  # in_competitions
            {TEST_COMPETITION_CODE: {FlagName.WAIT_INIT: False}},  # in_flags
            {},  # in_queue
            {  # expected_kafka
                DEFAULT_NOTIFICATIONS_TOPIC: [],
                DEFAULT_RAW_MESSAGES_TOPIC: [
                    Message(
                        competition_code=TEST_COMPETITION_CODE,
                        data=load_raw_message(
                            'endurance_status_finished.txt').strip(),
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
                            type=ActionType.UPDATE_COMPETITION_METADATA_STATUS,
                            data=UpdateCompetitionMetadataStatus(
                                competition_code=TEST_COMPETITION_CODE,
                                status=CompetitionStatus.FINISHED,
                            ),
                        ),
                        source=MessageSource.SOURCE_WS_LISTENER,
                        decoder=MessageDecoder.ACTION,
                        created_at=datetime.utcnow().timestamp(),
                        updated_at=datetime.utcnow().timestamp(),
                        error_description=None,
                        error_traceback=None,
                    ).encode(),
                ],
            },
            {},  # expected_queue
            {  # expected_flags
                TEST_COMPETITION_CODE: {FlagName.WAIT_INIT: False},
            },
        ),
        # Test case: When the flag 'wait-init' is disabled and it receives a
        # new message with a pit-in.
        (
            {  # kafka_topics
                DEFAULT_NOTIFICATIONS_TOPIC: [],
                DEFAULT_RAW_MESSAGES_TOPIC: [
                    Message(
                        competition_code=TEST_COMPETITION_CODE,
                        data=load_raw_message('endurance_pit_in.txt').strip(),
                        source=MessageSource.SOURCE_WS_LISTENER,
                        created_at=datetime.utcnow().timestamp(),
                        updated_at=datetime.utcnow().timestamp(),
                        error_description=None,
                        error_traceback=None,
                    ).encode(),
                ],
                DEFAULT_STD_MESSAGES_TOPIC: [],
            },
            {},  # in_competitions
            {TEST_COMPETITION_CODE: {FlagName.WAIT_INIT: False}},  # in_flags
            {},  # in_queue
            {  # expected_kafka
                DEFAULT_NOTIFICATIONS_TOPIC: [],
                DEFAULT_RAW_MESSAGES_TOPIC: [
                    Message(
                        competition_code=TEST_COMPETITION_CODE,
                        data=load_raw_message('endurance_pit_in.txt').strip(),
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
                            type=ActionType.ADD_PIT_IN,
                            data=AddPitIn(
                                id=1,
                                competition_code=TEST_COMPETITION_CODE,
                                driver_id=None,
                                team_id=1,
                                lap=0,
                                pit_time=0,
                                kart_status=KartStatus.UNKNOWN,
                            ),
                        ),
                        source=MessageSource.SOURCE_WS_LISTENER,
                        decoder=MessageDecoder.ACTION,
                        created_at=datetime.utcnow().timestamp(),
                        updated_at=datetime.utcnow().timestamp(),
                        error_description=None,
                        error_traceback=None,
                    ).encode(),
                ],
            },
            {},  # expected_queue
            {  # expected_flags
                TEST_COMPETITION_CODE: {FlagName.WAIT_INIT: False},
            },
        ),
        # Test case: When the flag 'wait-init' is disabled and it receives a
        # new message with a pit-out.
        (
            {  # kafka_topics
                DEFAULT_NOTIFICATIONS_TOPIC: [],
                DEFAULT_RAW_MESSAGES_TOPIC: [
                    Message(
                        competition_code=TEST_COMPETITION_CODE,
                        data=load_raw_message('endurance_pit_out.txt').strip(),
                        source=MessageSource.SOURCE_WS_LISTENER,
                        created_at=datetime.utcnow().timestamp(),
                        updated_at=datetime.utcnow().timestamp(),
                        error_description=None,
                        error_traceback=None,
                    ).encode(),
                ],
                DEFAULT_STD_MESSAGES_TOPIC: [],
            },
            {},  # in_competitions
            {TEST_COMPETITION_CODE: {FlagName.WAIT_INIT: False}},  # in_flags
            {},  # in_queue
            {  # expected_kafka
                DEFAULT_NOTIFICATIONS_TOPIC: [],
                DEFAULT_RAW_MESSAGES_TOPIC: [
                    Message(
                        competition_code=TEST_COMPETITION_CODE,
                        data=load_raw_message('endurance_pit_out.txt').strip(),
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
                            type=ActionType.ADD_PIT_OUT,
                            data=AddPitOut(
                                id=1,
                                competition_code=TEST_COMPETITION_CODE,
                                driver_id=None,
                                team_id=1,
                                kart_status=KartStatus.UNKNOWN,
                            ),
                        ),
                        source=MessageSource.SOURCE_WS_LISTENER,
                        decoder=MessageDecoder.ACTION,
                        created_at=datetime.utcnow().timestamp(),
                        updated_at=datetime.utcnow().timestamp(),
                        error_description=None,
                        error_traceback=None,
                    ).encode(),
                ],
            },
            {},  # expected_queue
            {  # expected_flags
                TEST_COMPETITION_CODE: {FlagName.WAIT_INIT: False},
            },
        ),
        # Test case: When the flag 'wait-init' is disabled and it receives a
        # new message with a timing position.
        (
            {  # kafka_topics
                DEFAULT_NOTIFICATIONS_TOPIC: [],
                DEFAULT_RAW_MESSAGES_TOPIC: [
                    Message(
                        competition_code=TEST_COMPETITION_CODE,
                        data=load_raw_message(
                            'endurance_timing_position.txt').strip(),
                        source=MessageSource.SOURCE_WS_LISTENER,
                        created_at=datetime.utcnow().timestamp(),
                        updated_at=datetime.utcnow().timestamp(),
                        error_description=None,
                        error_traceback=None,
                    ).encode(),
                ],
                DEFAULT_STD_MESSAGES_TOPIC: [],
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
            },
            {TEST_COMPETITION_CODE: {FlagName.WAIT_INIT: False}},  # in_flags
            {},  # in_queue
            {  # expected_kafka
                DEFAULT_NOTIFICATIONS_TOPIC: [],
                DEFAULT_RAW_MESSAGES_TOPIC: [
                    Message(
                        competition_code=TEST_COMPETITION_CODE,
                        data=load_raw_message(
                            'endurance_timing_position.txt').strip(),
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
                            type=ActionType.UPDATE_TIMING_POSITION,
                            data=UpdateTimingPosition(
                                competition_code=TEST_COMPETITION_CODE,
                                team_id=1,
                                position=6,
                                auto_other_positions=True,
                            ),
                        ),
                        source=MessageSource.SOURCE_WS_LISTENER,
                        decoder=MessageDecoder.ACTION,
                        created_at=datetime.utcnow().timestamp(),
                        updated_at=datetime.utcnow().timestamp(),
                        error_description=None,
                        error_traceback=None,
                    ).encode(),
                ],
            },
            {},  # expected_queue
            {  # expected_flags
                TEST_COMPETITION_CODE: {FlagName.WAIT_INIT: False},
            },
        ),
        # Test case: When the flag 'wait-init' is disabled and it receives a
        # new message with a timing position.
        (
            {  # kafka_topics
                DEFAULT_NOTIFICATIONS_TOPIC: [],
                DEFAULT_RAW_MESSAGES_TOPIC: [
                    Message(
                        competition_code=TEST_COMPETITION_CODE,
                        data=load_raw_message(
                            'endurance_stage_remaining_time_text.txt').strip(),
                        source=MessageSource.SOURCE_WS_LISTENER,
                        created_at=datetime.utcnow().timestamp(),
                        updated_at=datetime.utcnow().timestamp(),
                        error_description=None,
                        error_traceback=None,
                    ).encode(),
                ],
                DEFAULT_STD_MESSAGES_TOPIC: [],
            },
            {  # in_competitions
                TEST_COMPETITION_CODE: CompetitionInfo(
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings=PARSERS_SETTINGS,
                    drivers=[],
                    teams=[],
                    timing=[],
                ),
            },
            {TEST_COMPETITION_CODE: {FlagName.WAIT_INIT: False}},  # in_flags
            {},  # in_queue
            {  # expected_kafka
                DEFAULT_NOTIFICATIONS_TOPIC: [],
                DEFAULT_RAW_MESSAGES_TOPIC: [
                    Message(
                        competition_code=TEST_COMPETITION_CODE,
                        data=load_raw_message(
                            'endurance_stage_remaining_time_text.txt').strip(),
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
                            type=ActionType.UPDATE_COMPETITION_METADATA_REMAINING,  # noqa: E501, LN001
                            data=UpdateCompetitionMetadataRemaining(
                                competition_code=TEST_COMPETITION_CODE,
                                remaining_length={
                                    'value': 1200000,
                                    'unit': LengthUnit.MILLIS,
                                },
                            ),
                        ),
                        source=MessageSource.SOURCE_WS_LISTENER,
                        decoder=MessageDecoder.ACTION,
                        created_at=datetime.utcnow().timestamp(),
                        updated_at=datetime.utcnow().timestamp(),
                        error_description=None,
                        error_traceback=None,
                    ).encode(),
                ],
            },
            {},  # expected_queue
            {  # expected_flags
                TEST_COMPETITION_CODE: {FlagName.WAIT_INIT: False},
            },
        ),
    ],
)
def test_main(
        mocker: MockerFixture,
        kafka_topics: Dict[str, List[str]],
        in_competitions: Dict[str, CompetitionInfo],
        in_flags: Dict[str, Dict[FlagName, Any]],
        in_queue: Dict[str, List[Message]],
        expected_kafka: Dict[str, List[str]],
        expected_queue: Dict[str, List[Message]],
        expected_flags: dict) -> None:
    """Test main method."""
    with tempfile.TemporaryDirectory() as tmp_path:
        config = ParserConfig(
            api_lts=MOCK_API_LTS,
            errors_path=tmp_path,
            kafka_servers=MOCK_KAFKA,
            unknowns_path=tmp_path,
        )

        _apply_mock_api(mocker, MOCK_API_LTS)
        _mock_multiprocessing_process(mocker)
        mock_multiprocessing_dict(
            mocker, initial_dicts=[in_competitions, in_flags, in_queue])
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
        url=f'{api_url}/v1/c/filter/code/{TEST_COMPETITION_CODE}',
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
                'value': 'c5',
                'insert_date': '2023-04-15T21:43:26',
                'update_date': '2023-04-15T21:43:26',
            },
            {
                'name': ParserSettings.TIMING_POSITION.value,
                'value': 'c3',
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


def _mock_response_get_drivers(api_url: str) -> List[MapRequestItem]:
    """Get mocked response."""
    response = MockResponse(
        content=[
            {
                'id': 1,
                'competition_id': 1,
                'team_id': 1,
                'participant_code': 'r5625',
                'name': 'OTHER DRIVER',
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
                'participant_code': 'r5625',
                'name': 'DIMAS MUNOZ',
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


def _mock_response_get_teams(api_url: str) -> List[MapRequestItem]:
    """Get mocked response."""
    response = MockResponse(
        content=[
            {
                'id': 1,
                'competition_id': 1,
                'participant_code': 'r5625',
                'name': 'CKM 1',
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


def _apply_mock_api(mocker: MockerFixture, api_url: str) -> None:
    """Apply mock to API."""
    api_url = api_url.strip('/')
    requests_map = (
        _mock_response_auth_key(api_url)
        + _mock_response_get_competition_info(api_url)
        + _mock_response_get_drivers(api_url)
        + _mock_response_get_parser_settings(api_url)
        + _mock_response_get_teams(api_url))
    mock_requests(mocker, requests_map=requests_map)

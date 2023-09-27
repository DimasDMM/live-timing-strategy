from datetime import datetime
import pytest
from pytest_mock import MockerFixture
import tempfile
from typing import Dict, List

from ltspipe.configs import (
    WsParserConfig,
    DEFAULT_NOTIFICATIONS_TOPIC,
)
from ltspipe.data.notifications import Notification, NotificationType
from ltspipe.messages import Message, MessageDecoder, MessageSource
from ltspipe.runners.ws_parser.main import main
from tests.conftest import (
    mock_kafka_consumer_builder,
    mock_kafka_producer_builder,
    mock_websocket_builder,
)
from tests.fixtures import (
    REAL_API_LTS,
    MOCK_KAFKA,
    MOCK_WS,
    TEST_COMPETITION_CODE,
)
from tests.helpers import (
    load_raw_message,
    DatabaseTest,
    DatabaseContent,
    TableContent,
)
from tests.mocks.logging import FakeLogger
from tests.mocks.multiprocessing import MockProcess

EXCLUDED_KEYS = {
    'created_at': True,
    'updated_at': True,
}


def _mock_multiprocessing_process(mocker: MockerFixture) -> None:
    """Mock parallel processes by sequential ones."""
    mocker.patch(
        'ltspipe.runners.ws_parser.main._create_process',
        new=MockProcess)


class TestMain(DatabaseTest):
    """
    Functional test of ltspipe.runners.ws_parser.main.

    Important: Since these tests are functional, they require that there are
    a database and an API REST running.
    """

    @pytest.mark.parametrize(
        ('database_content, kafka_topics, in_websocket,'
         'expected_kafka, expected_database'),
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
                {  # kafka_topics
                    DEFAULT_NOTIFICATIONS_TOPIC: [],
                },
                [  # in_websocket
                    load_raw_message('init_endurance.txt'),
                ],
                {  # expected_kafka
                    DEFAULT_NOTIFICATIONS_TOPIC: [
                        Message(
                            competition_code=TEST_COMPETITION_CODE,
                            data=Notification(
                                type=NotificationType.INITIALIZED_COMPETITION,
                            ),
                            source=MessageSource.SOURCE_WS_LISTENER,
                            created_at=datetime.utcnow().timestamp(),
                            updated_at=datetime.utcnow().timestamp(),
                            decoder=MessageDecoder.NOTIFICATION,
                        ).encode(),
                    ],
                },
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
                                    'race',
                                    10791671,
                                    'millis'
                                ],
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
                                [1, 'r5626', 'Team 2', 42, None],
                                [1, 'r5627', 'Team 3', 43, None],
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
                                    None,  # driver_id
                                    1,  # position
                                    0,  # last_time
                                    0,  # best_time
                                    0,  # lap
                                    None,  # gap
                                    None,  # gap_unit
                                    None,  # interval
                                    None,  # interval_unit
                                    'race',  # stage
                                    0,  # pit_time
                                    'unknown',  # kart_status
                                    None,  # fixed_kart_status
                                    0,  # number_pits
                                ],
                                [
                                    1,  # competition_id
                                    2,  # team_id
                                    None,  # driver_id
                                    2,  # position
                                    0,  # last_time
                                    0,  # best_time
                                    0,  # lap
                                    None,  # gap
                                    None,  # gap_unit
                                    None,  # interval
                                    None,  # interval_unit
                                    'race',  # stage
                                    0,  # pit_time
                                    'unknown',  # kart_status
                                    None,  # fixed_kart_status
                                    0,  # number_pits
                                ],
                                [
                                    1,  # competition_id
                                    3,  # team_id
                                    None,  # driver_id
                                    3,  # position
                                    0,  # last_time
                                    0,  # best_time
                                    0,  # lap
                                    None,  # gap
                                    None,  # gap_unit
                                    None,  # interval
                                    None,  # interval_unit
                                    'race',  # stage
                                    0,  # pit_time
                                    'unknown',  # kart_status
                                    None,  # fixed_kart_status
                                    0,  # number_pits
                                ],
                            ],
                        ),
                    ],
                ),
            ),
        ],
    )
    def test_main(
            self,
            mocker: MockerFixture,
            database_content: DatabaseContent,
            kafka_topics: Dict[str, List[str]],
            in_websocket: List[str],
            expected_kafka: Dict[str, List[str]],
            expected_database: DatabaseContent) -> None:
        """
        Test main method.

        Test case: it receives an action with data to initialize in the API REST.
        After it sends the data to the API, it should generate a notification.
        """
        with tempfile.TemporaryDirectory() as tmp_path:
            self.set_database_content(database_content)
            config = WsParserConfig(
                api_lts=REAL_API_LTS,
                competition_code=TEST_COMPETITION_CODE,
                errors_path=tmp_path,
                kafka_servers=MOCK_KAFKA,
                unknowns_path=tmp_path,
                websocket_uri=MOCK_WS,
            )

            _mock_multiprocessing_process(mocker)
            mock_kafka_consumer_builder(mocker, kafka_topics=kafka_topics)
            mock_kafka_producer_builder(mocker, kafka_topics=kafka_topics)
            mock_websocket_builder(mocker, messages=in_websocket)
            fake_logger = FakeLogger()

            main(config=config, logger=fake_logger)

            # Validate that the messages are received by Kafka
            out_kafka = {topic: self._raw_to_dict(raw)
                        for topic, raw in kafka_topics.items()}
            assert (out_kafka == {topic: self._raw_to_dict(raw)
                                for topic, raw in expected_kafka.items()})

            # Validate database content
            query = expected_database.to_query()
            assert (self.get_database_content(query).model_dump() ==
                    expected_database.model_dump())

    def _raw_to_dict(self, raw: List[str]) -> List[dict]:
        """Transform messages into dictionaries."""
        return [Message.decode(x).model_dump(exclude=EXCLUDED_KEYS)
                for x in raw]

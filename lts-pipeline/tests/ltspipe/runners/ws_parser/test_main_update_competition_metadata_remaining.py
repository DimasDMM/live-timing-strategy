from datetime import datetime
import pytest
from pytest_mock import MockerFixture
import tempfile
from typing import Dict, List

from ltspipe.configs import (
    WsParserConfig,
    DEFAULT_NOTIFICATIONS_TOPIC,
)
from ltspipe.data.competitions import (
    CompetitionMetadata,
    CompetitionStage,
    CompetitionStatus,
    DiffLap,
)
from ltspipe.data.enum import LengthUnit
from ltspipe.data.notifications import Notification, NotificationType
from ltspipe.messages import Message, MessageDecoder, MessageSource
from ltspipe.runners.ws_parser.main import main
from tests.conftest import (
    mock_kafka_consumer_builder,
    mock_kafka_producer_builder,
    mock_websocket_builder,
)
from tests.fixtures import (
    API_LTS,
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
                                    'ongoing',
                                    'race',
                                    3600000,
                                    'millis',
                                ],
                            ],
                        ),
                        TableContent(
                            table_name='competitions_metadata_history',
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
                                    'ongoing',
                                    'race',
                                    3600000,
                                    'millis',
                                ],
                            ],
                        ),
                    ],
                ),
                {  # kafka_topics
                    DEFAULT_NOTIFICATIONS_TOPIC: [],
                },
                [  # in_websocket
                    load_raw_message(
                        'endurance_stage_remaining_time_countdown.txt'),
                ],
                {  # expected_kafka
                    DEFAULT_NOTIFICATIONS_TOPIC: [
                        Message(
                            competition_code=TEST_COMPETITION_CODE,
                            data=Notification(
                                type=NotificationType.UPDATED_COMPETITION_METADATA_REMAINING,  # noqa: E501, LN001
                                data=CompetitionMetadata(
                                    stage=CompetitionStage.RACE,
                                    status=CompetitionStatus.ONGOING,
                                    remaining_length=DiffLap(
                                        value=10761515,
                                        unit=LengthUnit.MILLIS,
                                    ),
                                ),
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
                                    'ongoing',
                                    'race',
                                    10761515,
                                    'millis',
                                ],
                            ],
                        ),
                        TableContent(
                            table_name='competitions_metadata_history',
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
                                    'ongoing',
                                    'race',
                                    3600000,
                                    'millis',
                                ],
                                [
                                    1,
                                    None,
                                    None,
                                    'ongoing',
                                    'race',
                                    10761515,
                                    'millis',
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
        """Test main method."""
        with tempfile.TemporaryDirectory() as tmp_path:
            self.set_database_content(database_content)
            config = WsParserConfig(
                api_lts=API_LTS,
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
            assert self.get_database_content(query) == expected_database

    def _raw_to_dict(self, raw: List[str]) -> List[dict]:
        """Transform messages into dictionaries."""
        return [Message.decode(x).model_dump(exclude=EXCLUDED_KEYS)
                for x in raw]

from typing import List
from unittest.mock import MagicMock

from pyback.messages import Message
from pyback.steps.loggers import LogInfoStep
from tests.mocks.logging import FakeLogger


def test_log_info_step(sample_message: Message) -> None:
    """Test messages through LogInfoStep."""
    next_step = MagicMock()
    fake_logger = FakeLogger()
    log_step = LogInfoStep(logger=fake_logger, next_step=next_step)
    log_step.run_step(sample_message)

    # Assert that the logger receives the message
    expected_start = (
        '{"event_code": "' + sample_message.get_event_code()
        + '", "data": "' + sample_message.get_data() + '"')
    messages: List[str] = fake_logger.get_messages()['info']
    assert len(messages) == 1
    assert messages[0].startswith(expected_start)

    # Assert that the next step is called
    next_step.run_step.assert_called_once_with(sample_message)

import os
from pytest_mock import MockerFixture
import tempfile
from unittest.mock import MagicMock

from ltspipe.messages import Message
from ltspipe.steps.filesystem import MessageStorageStep, RawStorageStep
from tests.fixtures import TEST_COMPETITION_CODE
from tests.mocks.logging import FakeLogger

EXCLUDED_KEYS = {'updated_at': True}


class TestMessageStorageStep:
    """Test ltspipe.steps.listeners.MessageStorageStep class."""

    def test_start_step(
            self, mocker: MockerFixture, sample_message: Message) -> None:
        """Test method run_step."""
        with tempfile.TemporaryDirectory() as tmp_path:
            # Apply mock to input() function
            return_time = 1
            mocker.patch('time.time', return_value=return_time)

            # Create a mock of the next step
            next_step = MagicMock()
            next_step.get_children.return_value = []

            # Create an instance of FileListenerStep
            fake_logger = FakeLogger()
            step = MessageStorageStep(
                logger=fake_logger,
                output_path=tmp_path,
                next_step=next_step,
            )

            # Call run_step with a dummy message and validate that the next step
            # has received it
            step.run_step(sample_message)
            assert next_step.run_step.call_count == 1
            received_msg: Message = next_step.run_step.call_args_list[0][0][0]
            assert received_msg.competition_code == TEST_COMPETITION_CODE
            assert received_msg.data == sample_message.data

            # Validate that the message was stored correctly
            expected_file = os.path.join(tmp_path, f'{return_time}.msg.txt')
            assert os.path.exists(expected_file)
            with open(expected_file, 'r') as fp:
                content = fp.read()
                found_message: Message = Message.decode(content)  # type: ignore
                assert (found_message.model_dump(exclude=EXCLUDED_KEYS)
                        == sample_message.model_dump(exclude=EXCLUDED_KEYS))

            # Also, check that the get_children method returns the mocks
            children = step.get_children()
            assert children == [next_step]


class TestRawStorageStep:
    """Test ltspipe.steps.listeners.RawStorageStep class."""

    def test_start_step(
            self, mocker: MockerFixture, sample_message: Message) -> None:
        """Test method run_step."""
        with tempfile.TemporaryDirectory() as tmp_path:
            # Apply mock to input() function
            return_time = 1
            mocker.patch('time.time', return_value=return_time)

            # Create a mock of the next step
            next_step = MagicMock()
            next_step.get_children.return_value = []

            # Create an instance of FileListenerStep
            fake_logger = FakeLogger()
            step = RawStorageStep(
                logger=fake_logger,
                output_path=tmp_path,
                next_step=next_step,
            )

            # Call run_step with a dummy message and validate that the next step
            # has received it
            step.run_step(sample_message)
            assert next_step.run_step.call_count == 1
            received_msg: Message = next_step.run_step.call_args_list[0][0][0]
            assert received_msg.competition_code == TEST_COMPETITION_CODE
            assert received_msg.data == sample_message.data

            # Validate that the message was stored correctly
            expected_file = os.path.join(tmp_path, f'{return_time}.raw.txt')
            assert os.path.exists(expected_file)
            with open(expected_file, 'r') as fp:
                content = fp.read()
                assert content == sample_message.data

            # Also, check that the get_children method returns the mocks
            children = step.get_children()
            assert children == [next_step]

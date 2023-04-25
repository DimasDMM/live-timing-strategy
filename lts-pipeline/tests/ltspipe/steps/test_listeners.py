from pytest_mock import MockerFixture
import tempfile
from unittest.mock import MagicMock

from ltspipe.messages import Message, MessageSource
from ltspipe.steps.listeners import FileListenerStep
from tests.fixtures import TEST_COMPETITION_CODE
from tests.mocks.logging import FakeLogger


class TestFileListenerStep:
    """Test ltspipe.steps.listeners.FileListenerStep class."""

    def test_start_step(self, mocker: MockerFixture) -> None:
        """Test method run_step."""
        with tempfile.TemporaryDirectory() as tmp_path:
            # Apply mock to input() function
            sample_data = 'Hello, World!'
            file_path = self._create_sample_file(tmp_path, sample_data)
            mocker.patch('builtins.input', return_value=file_path)

            # Create a mock of the next step
            next_step = MagicMock()
            next_step.get_children.return_value = []

            # Create an instance of FileListenerStep
            fake_logger = FakeLogger()
            step = FileListenerStep(
                logger=fake_logger,
                competition_code=TEST_COMPETITION_CODE,
                single_file=True,
                infinite_loop=False,
                message_source=MessageSource.SOURCE_DUMMY,
                next_step=next_step,
            )

            # Call start_step and validate that the next step has received it
            step.start_step()
            assert next_step.run_step.call_count == 1
            received_msg: Message = next_step.run_step.call_args_list[0][0][0]
            assert received_msg.competition_code == TEST_COMPETITION_CODE
            assert received_msg.data == sample_data

            # Also, check that the get_children method returns the mocks
            children = step.get_children()
            assert children == [next_step]

    def test_start_step_without_file(self, mocker: MockerFixture) -> None:
        """Test method run_step."""
        # Apply mock to input() function
        file_path = 'unknown/file.txt'
        mocker.patch('builtins.input', return_value=file_path)

        # Create a mock of the next step
        next_step = MagicMock()
        next_step.get_children.return_value = []

        # Create an instance of FileListenerStep
        fake_logger = FakeLogger()
        step = FileListenerStep(
            logger=fake_logger,
            competition_code=TEST_COMPETITION_CODE,
            single_file=True,
            infinite_loop=False,
            message_source=MessageSource.SOURCE_DUMMY,
            next_step=next_step,
        )

        # Call start_step and validate that the next step did not receive
        # anything
        step.start_step()
        assert next_step.run_step.call_count == 0

        # Also, check that the get_children method returns the mocks
        children = step.get_children()
        assert children == [next_step]

    def _create_sample_file(self, path: str, content: str) -> str:
        """Create a file with some sample content."""
        file_path = f'{path}/myfile.txy'
        with open(file_path, 'w') as fp:
            fp.write(content)
        return file_path

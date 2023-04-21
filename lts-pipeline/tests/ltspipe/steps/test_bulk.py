from typing import Dict, List
from unittest.mock import MagicMock

from ltspipe.data.enum import FlagName
from ltspipe.messages import Message, MessageSource
from ltspipe.steps.bulk import QueueDistributorStep, QueueForwardStep
from tests.mocks.logging import FakeLogger


class TestQueueDistributor:
    """Test ltspipe.steps.bulk.QueueDistributor class."""

    def test_run_step(self, sample_message: Message) -> None:
        """Test method run_step."""
        # Create a mock of the next step
        next_step = MagicMock()
        next_step.get_children.return_value = []

        # Create an instance of QueueDistributor
        competition_code = sample_message.competition_code
        in_flags = {competition_code: {FlagName.WAIT_INIT: False}}
        in_queue: Dict[str, List[Message]] = {}
        fake_logger = FakeLogger()
        step = QueueDistributorStep(
            logger=fake_logger,
            flags=in_flags,
            flag_name=FlagName.WAIT_INIT,
            queue=in_queue,
            next_step=next_step)

        # Call run_step with a dummy message and validate that the next step
        # has received it
        step.run_step(sample_message)

        assert next_step.run_step.call_count == 1
        assert in_queue == {}  # Empty queue
        received_msg: Message = next_step.run_step.call_args_list[0][0][0]
        assert received_msg.competition_code == competition_code
        assert received_msg.data == sample_message.data

        # Set wait_init to True, call run_step with a dummy message and validate
        # that the message has entered into the queue
        in_flags[competition_code][FlagName.WAIT_INIT] = True
        step.run_step(sample_message)

        assert next_step.run_step.call_count == 1  # Same as previous
        assert competition_code in in_queue
        assert len(in_queue[competition_code]) == 1
        queue_msg = in_queue[competition_code][0]
        assert queue_msg.competition_code == competition_code
        assert queue_msg.data == sample_message.data

        # Also, check that the get_children method returns the mock
        children = step.get_children()
        assert children == [next_step]


class TestQueueForwardStep:
    """Test ltspipe.steps.bulk.QueueForwardStep class."""

    _msg_counter: int = 0

    def _build_message(self) -> Message:
        """Build a sample message."""
        data = {'counter': self._msg_counter}
        self._msg_counter += 1
        return Message(
            competition_code='sample-code',
            data=data,
            source=MessageSource.SOURCE_DUMMY,
            created_at=1679944690.8801994,
            updated_at=1679944719.1858709,
            error_description=None,
            error_traceback=None,
        )

    def test_run_step(self) -> None:
        """Test method run_step."""
        step_message = self._build_message()
        competition_code = step_message.competition_code

        # Create a mock of the next steps
        next_step = MagicMock()
        next_step.get_children.return_value = []

        queue_step = MagicMock()
        queue_step.get_children.return_value = []

        # Init queue with 2 sample messages
        initial_queue = {
            competition_code: [self._build_message(), self._build_message()]}
        copy_queue = initial_queue.copy()

        # Create an instance of QueueForwardStep
        fake_logger = FakeLogger()
        step = QueueForwardStep(
            logger=fake_logger,
            queue=initial_queue,
            queue_step=queue_step,
            next_step=next_step)

        # Call run_step with a dummy message and validate that:
        # - The next step has received it
        # - All the messages in the queue are forwarded to the queue_step
        # - The queue is empty after it
        step.run_step(step_message)

        assert initial_queue == {competition_code: []}  # Queue is empty

        assert next_step.run_step.call_count == 1
        received_msg: Message = next_step.run_step.call_args_list[0][0][0]
        assert received_msg.competition_code == step_message.competition_code
        assert received_msg.data == step_message.data

        assert queue_step.run_step.call_count == 2
        for i, initial_msg in enumerate(copy_queue[competition_code]):
            received_msg = queue_step.run_step.call_args_list[i][0][0]
            assert received_msg.competition_code == initial_msg.competition_code
            assert received_msg.data == initial_msg.data

        # Also, check that the get_children method returns the mock
        children = step.get_children()
        assert children == [queue_step, next_step]

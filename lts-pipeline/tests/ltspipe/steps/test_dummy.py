from unittest.mock import MagicMock

from ltspipe.messages import Message
from ltspipe.steps.dummy import DummyStartStep, NullStep


def test_dummy_start_step(n_messages: int = 2) -> None:
    """Test ltspipe.steps.dummy.DummyStartStep."""
    # Create a mock of the next step
    next_step = MagicMock()
    next_step.get_children.return_value = []

    # Create an instance of DummyStartStep and call start_step
    dummy_start_step = DummyStartStep(
        next_step=next_step, n_messages=n_messages)
    dummy_start_step.start_step()

    # Check that the next_step was called twice with the expected arguments
    assert next_step.run_step.call_count == 2
    message: Message = None
    for i in range(n_messages):
        message = next_step.run_step.call_args_list[i][0][0]
        assert message.competition_code == DummyStartStep.DUMMY_CODE
        assert message.data == {'counter': i}

    # Also, check that the get_children method returns the mock
    children = dummy_start_step.get_children()
    assert children == [next_step]


def test_null_step(sample_message: Message) -> None:
    """Test messages through NullStep."""
    # Create a mock of the next step
    next_step = MagicMock()
    next_step.get_children.return_value = []

    # Create an instance of NullStep and call run_step
    null_step = NullStep(next_step=next_step)
    null_step.run_step(sample_message)

    # Check that the next_step was called twice with the expected arguments
    assert next_step.run_step.call_count == 1
    message: Message = next_step.run_step.call_args_list[0][0][0]
    assert message.competition_code == sample_message.competition_code
    assert message.data == sample_message.data

    # Also, check that the get_children method returns the mock
    children = null_step.get_children()
    assert children == [next_step]

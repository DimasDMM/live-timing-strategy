from unittest.mock import MagicMock

from pyback.messages import Message
from pyback.steps.dummy import DummyStartStep


def test_dummy_start_step(n_messages: int = 2) -> None:
    """Test pyback.steps.dummy.DummyStartStep."""
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
        assert message.get_event_code() == DummyStartStep.DUMMY_CODE
        assert message.get_data() == {'counter': i}

    # Also, check that the get_children method returns the mock
    children = dummy_start_step.get_children()
    assert children == [next_step]

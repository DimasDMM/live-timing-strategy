from datetime import datetime
from unittest.mock import MagicMock

from ltspipe.data.notifications import Notification, NotificationType
from ltspipe.messages import Message, MessageDecoder, MessageSource
from ltspipe.steps.strategy import StrategyStep
from tests.fixtures import TEST_COMPETITION_CODE
from tests.helpers import build_magic_parser, build_magic_step
from tests.mocks.logging import FakeLogger


class TestStrategyStep:
    """Test ltspipe.steps.notifications.StrategyStep class."""

    def _build_notification(self, ntype: NotificationType) -> Message:
        """Build a notification of init data."""
        return Message(
            competition_code=TEST_COMPETITION_CODE,
            data=Notification(type=ntype),
            source=MessageSource.SOURCE_DUMMY,
            decoder=MessageDecoder.NOTIFICATION,
            created_at=datetime.utcnow().timestamp(),
            updated_at=datetime.utcnow().timestamp(),
        )

    def test_run_step(self, sample_message: Message) -> None:
        """Test method run_step."""
        # Create a mock of the next step
        parser, _ = build_magic_parser()
        on_parsed = build_magic_step()
        on_unknown = build_magic_step()

        # Create an instance of StrategyStep
        fake_logger = FakeLogger()
        step = StrategyStep(
            logger=fake_logger,
            parser=parser,
            on_parsed=on_parsed,
            on_unknown=on_unknown,
        )

        # Proceed with the test in the step
        self._first_step(step, on_parsed, on_unknown, sample_message)
        self._second_step(
            step,
            on_parsed,
            on_unknown,
            self._build_notification(NotificationType.ADDED_PIT_IN),
        )

        # Also, check that the get_children method returns the mocks
        children = step.get_children()
        assert children == [on_parsed, on_unknown]

    def _first_step(
            self,
            step: StrategyStep,
            on_parsed: MagicMock,
            on_other: MagicMock,
            normal_msg: Message) -> None:
        # When the message is something not related to notifications
        step.run_step(normal_msg)
        assert on_parsed.run_step.call_count == 0
        assert on_other.run_step.call_count == 0

    def _second_step(
            self,
            step: StrategyStep,
            on_parsed: MagicMock,
            on_other: MagicMock,
            notification: Message) -> None:
        # When the message is about anything else but the mapped notifications,
        # it goes to the step 'on_other'
        step.run_step(notification)
        assert on_parsed.run_step.call_count == 1
        assert on_other.run_step.call_count == 0
        received_msg: Message = on_parsed.run_step.call_args_list[0][0][0]
        assert received_msg.competition_code == TEST_COMPETITION_CODE

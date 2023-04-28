from datetime import datetime
from unittest.mock import MagicMock

from ltspipe.data.notifications import Notification, NotificationType
from ltspipe.messages import Message, MessageDecoder, MessageSource
from ltspipe.steps.triggers import WsInitTriggerStep
from tests.fixtures import TEST_COMPETITION_CODE
from tests.helpers import build_magic_step
from tests.mocks.logging import FakeLogger


class TestWsInitTriggerStep:
    """Test ltspipe.steps.triggers.WsInitTriggerStep class."""

    def _build_init_message(self) -> Message:
        """Build a sample message."""
        return Message(
            competition_code=TEST_COMPETITION_CODE,
            data='init|r|this-is-an-initializer',
            source=MessageSource.SOURCE_DUMMY,
            created_at=1679944690.8801994,
            updated_at=1679944719.1858709,
        )

    def _build_normal_message(self) -> Message:
        """Build a sample message."""
        return Message(
            competition_code=TEST_COMPETITION_CODE,
            data='sample-data',
            source=MessageSource.SOURCE_DUMMY,
            created_at=1679944690.8801994,
            updated_at=1679944719.1858709,
        )

    def _build_notification(self) -> Message:
        """Build a notification of init data."""
        return Message(
            competition_code=TEST_COMPETITION_CODE,
            data=Notification(
                type=NotificationType.INIT_ONGOING,
            ),
            source=MessageSource.SOURCE_DUMMY,
            decoder=MessageDecoder.NOTIFICATION,
            created_at=datetime.utcnow().timestamp(),
            updated_at=datetime.utcnow().timestamp(),
        )

    def test_run_step(self) -> None:
        """Test method run_step."""
        # Create a mock of the next step
        on_init = build_magic_step()
        on_other = build_magic_step()
        trigger_step = build_magic_step()

        # Create sample messages
        init_msg = self._build_init_message()
        normal_msg = self._build_normal_message()
        notification = self._build_notification()

        # Create an instance of WsInitTriggerStep
        fake_logger = FakeLogger()
        step = WsInitTriggerStep(
            logger=fake_logger,
            on_init_trigger=trigger_step,
            on_init=on_init,
            on_other=on_other,
        )

        # Proceed with the test in three separated steps
        self._first_step(step, on_init, on_other, trigger_step, normal_msg)
        self._second_step(
            step, on_init, on_other, trigger_step, init_msg, notification)

        # Also, check that the get_children method returns the mocks
        children = step.get_children()
        assert children == [on_init, on_other, trigger_step]

    def _first_step(
            self,
            step: WsInitTriggerStep,
            on_init: MagicMock,
            on_other: MagicMock,
            notify_step: MagicMock,
            normal_msg: Message) -> None:
        # When the message contains normal data, it should go to the 'on_other'
        # step
        step.run_step(normal_msg)
        assert on_init.run_step.call_count == 0
        assert on_other.run_step.call_count == 1
        assert notify_step.run_step.call_count == 0
        received_msg: Message = on_other.run_step.call_args_list[0][0][0]
        assert received_msg.competition_code == normal_msg.competition_code
        assert received_msg.data == normal_msg.data

    def _second_step(
            self,
            step: WsInitTriggerStep,
            on_init: MagicMock,
            on_other: MagicMock,
            notify_step: MagicMock,
            init_msg: Message,
            notification: Message) -> None:
        # When the message contains initializer data, it should go to
        # the 'on_init' step and, also, send a notification to 'notify_step'
        step.run_step(init_msg)
        assert on_init.run_step.call_count == 1
        assert on_other.run_step.call_count == 1
        assert notify_step.run_step.call_count == 1

        received_msg: Message = on_init.run_step.call_args_list[0][0][0]
        assert received_msg.competition_code == init_msg.competition_code
        assert received_msg.data == init_msg.data

        received_msg = notify_step.run_step.call_args_list[0][0][0]
        assert received_msg.competition_code == notification.competition_code
        assert received_msg.data == notification.data

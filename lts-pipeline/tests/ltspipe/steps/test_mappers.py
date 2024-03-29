from datetime import datetime
from unittest.mock import MagicMock

from ltspipe.data.notifications import Notification, NotificationType
from ltspipe.messages import Message, MessageDecoder, MessageSource
from ltspipe.steps.mappers import NotificationMapperStep
from tests.fixtures import TEST_COMPETITION_CODE
from tests.helpers import build_magic_step
from tests.mocks.logging import FakeLogger


class TestNotificationMapperStep:
    """Test ltspipe.steps.notifications.NotificationMapperStep class."""

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
        notify_step = build_magic_step()
        on_other = build_magic_step()
        map_notification = {
            NotificationType.INIT_FINISHED: notify_step,
        }

        # Create an instance of NotificationMapperStep
        fake_logger = FakeLogger()
        step = NotificationMapperStep(
            logger=fake_logger,
            map_notification=map_notification,
            on_other=on_other,
        )

        # Proceed with the test in three separated steps
        self._first_step(step, notify_step, on_other, sample_message)
        self._second_step(
            step,
            notify_step,
            on_other,
            self._build_notification(NotificationType.ADDED_PIT_IN),
        )
        self._third_step(
            step,
            notify_step,
            on_other,
            self._build_notification(NotificationType.INIT_FINISHED),
        )

        # Also, check that the get_children method returns the mocks
        children = step.get_children()
        assert children == [on_other, notify_step]

    def _first_step(
            self,
            step: NotificationMapperStep,
            notify_step: MagicMock,
            on_other: MagicMock,
            normal_msg: Message) -> None:
        # When the message is something not related to notifications
        step.run_step(normal_msg)
        assert notify_step.run_step.call_count == 0
        assert on_other.run_step.call_count == 0

    def _second_step(
            self,
            step: NotificationMapperStep,
            notify_step: MagicMock,
            on_other: MagicMock,
            notification: Message) -> None:
        # When the message is about anything else but the mapped notifications,
        # it goes to the step 'on_other'
        step.run_step(notification)
        assert notify_step.run_step.call_count == 0
        assert on_other.run_step.call_count == 1
        received_msg: Message = on_other.run_step.call_args_list[0][0][0]
        assert received_msg.competition_code == TEST_COMPETITION_CODE
        assert received_msg.data == notification.data

    def _third_step(
            self,
            step: NotificationMapperStep,
            notify_step: MagicMock,
            on_other: MagicMock,
            notification: Message) -> None:
        # When the message is a mapped notification, it should go to the
        # appropiate notification step
        step.run_step(notification)
        assert notify_step.run_step.call_count == 1
        assert on_other.run_step.call_count == 1
        received_msg: Message = notify_step.run_step.call_args_list[0][0][0]
        assert received_msg.competition_code == TEST_COMPETITION_CODE
        assert received_msg.data == notification.data

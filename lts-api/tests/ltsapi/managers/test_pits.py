import pytest
import time
from typing import Optional

from ltsapi.db import DBContext
from ltsapi.managers.pits import (
    PitsInManager,
    PitsOutManager,
    TypeUpdatePitIn,
    TypeUpdatePitOut,
)
from ltsapi.models.enum import KartStatus
from ltsapi.models.pits import (
    AddPitIn,
    AddPitOut,
    UpdatePitIn,
    UpdatePitInDriver,
    UpdatePitInFixedKartStatus,
    UpdatePitInKartStatus,
    UpdatePitInPitTime,
    UpdatePitOut,
    UpdatePitOutDriver,
    UpdatePitOutFixedKartStatus,
    UpdatePitOutKartStatus,
)
from tests.helpers import DatabaseTest
from tests.mocks.logging import FakeLogger


class TestPitsInManager(DatabaseTest):
    """Test class ltsapi.managers.pits.PitsInManager."""

    EXCLUDE = {
        'insert_date': True,
        'update_date': True,
    }

    @pytest.mark.parametrize(
        'competition_id, expected_items',
        [
            (
                2,  # competition_id
                [
                    {
                        'id': 1,
                        'competition_id': 2,
                        'team_id': 4,
                        'driver_id': 5,
                        'lap': 1,
                        'pit_time': 150500,
                        'kart_status': KartStatus.UNKNOWN.value,
                        'fixed_kart_status': None,
                        'has_pit_out': True,
                    },
                    {
                        'id': 2,
                        'competition_id': 2,
                        'team_id': 5,
                        'driver_id': 7,
                        'lap': 1,
                        'pit_time': 151000,
                        'kart_status': KartStatus.UNKNOWN.value,
                        'fixed_kart_status': None,
                        'has_pit_out': True,
                    },
                    {
                        'id': 3,
                        'competition_id': 2,
                        'team_id': 5,
                        'driver_id': 7,
                        'lap': 3,
                        'pit_time': 150900,
                        'kart_status': KartStatus.UNKNOWN.value,
                        'fixed_kart_status': None,
                        'has_pit_out': False,
                    },
                ],
            ),
        ])
    def test_get_by_competition_id(
            self,
            competition_id: int,
            expected_items: list,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method get_by_competition_id."""
        manager = PitsInManager(db=db_context, logger=fake_logger)
        db_items = manager.get_by_competition_id(competition_id)
        dict_items = [x.model_dump(exclude=self.EXCLUDE) for x in db_items]
        assert dict_items == expected_items

    @pytest.mark.parametrize(
        'pit_in_id, competition_id, expected_item',
        [
            (
                1,  # pit_in_id
                None,  # competition_id
                {
                    'id': 1,
                    'competition_id': 2,
                    'team_id': 4,
                    'driver_id': 5,
                    'lap': 1,
                    'pit_time': 150500,
                    'kart_status': KartStatus.UNKNOWN.value,
                    'fixed_kart_status': None,
                    'has_pit_out': True,
                },
            ),
            (
                1,  # pit_in_id
                2,  # competition_id
                {
                    'id': 1,
                    'competition_id': 2,
                    'team_id': 4,
                    'driver_id': 5,
                    'lap': 1,
                    'pit_time': 150500,
                    'kart_status': KartStatus.UNKNOWN.value,
                    'fixed_kart_status': None,
                    'has_pit_out': True,
                },
            ),
        ])
    def test_get_by_id(
            self,
            pit_in_id: int,
            competition_id: Optional[int],
            expected_item: dict,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method get_by_id."""
        manager = PitsInManager(db=db_context, logger=fake_logger)

        db_item = manager.get_by_id(
            pit_in_id=pit_in_id, competition_id=competition_id)
        assert db_item is not None

        dict_item = db_item.model_dump(exclude=self.EXCLUDE)
        assert dict_item == expected_item

    @pytest.mark.parametrize(
        'competition_id, team_id, expected_items',
        [
            (
                2,  # competition_id
                4,  # team_id
                [
                    {
                        'id': 1,
                        'competition_id': 2,
                        'team_id': 4,
                        'driver_id': 5,
                        'lap': 1,
                        'pit_time': 150500,
                        'kart_status': KartStatus.UNKNOWN.value,
                        'fixed_kart_status': None,
                        'has_pit_out': True,
                    },
                ],
            ),
        ])
    def test_get_by_team_id(
            self,
            competition_id: int,
            team_id: int,
            expected_items: list,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method get_by_team_id."""
        manager = PitsInManager(db=db_context, logger=fake_logger)
        db_items = manager.get_by_team_id(competition_id, team_id)
        dict_items = [x.model_dump(exclude=self.EXCLUDE) for x in db_items]
        assert dict_items == expected_items

    @pytest.mark.parametrize(
        'competition_id, team_id, expected_item',
        [
            (
                2,  # competition_id
                5,  # team_id
                {  # expected_item
                    'id': 3,
                    'competition_id': 2,
                    'team_id': 5,
                    'driver_id': 7,
                    'lap': 3,
                    'pit_time': 150900,
                    'kart_status': KartStatus.UNKNOWN.value,
                    'fixed_kart_status': None,
                    'has_pit_out': False,
                },
            ),
        ])
    def test_get_last_by_team_id(
            self,
            competition_id: int,
            team_id: int,
            expected_item: dict,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method get_by_team_id."""
        manager = PitsInManager(db=db_context, logger=fake_logger)
        db_item = manager.get_last_by_team_id(competition_id, team_id)
        assert db_item is not None

        dict_item = db_item.model_dump(exclude=self.EXCLUDE)
        assert dict_item == expected_item

    @pytest.mark.parametrize(
        'competition_id, model, expected_item',
        [
            (
                2,  # competition_id
                AddPitIn(
                    team_id=5,
                    driver_id=7,
                    lap=4,
                    pit_time=None,
                    kart_status=KartStatus.GOOD,
                    fixed_kart_status=None,
                ),
                {
                    'id': None,
                    'competition_id': 2,
                    'team_id': 5,
                    'driver_id': 7,
                    'lap': 4,
                    'pit_time': None,
                    'kart_status': KartStatus.GOOD.value,
                    'fixed_kart_status': None,
                    'has_pit_out': False,
                },
            ),
        ])
    def test_add_one(
            self,
            competition_id: Optional[int],
            model: AddPitIn,
            expected_item: dict,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method add_one."""
        manager = PitsInManager(db=db_context, logger=fake_logger)
        item_id = manager.add_one(model, competition_id, commit=True)

        expected_item['id'] = item_id
        db_item = manager.get_by_id(item_id, competition_id)
        assert db_item is not None

        dict_item = db_item.model_dump(exclude=self.EXCLUDE)
        assert dict_item == expected_item

    @pytest.mark.parametrize(
        'pit_in_id, competition_id, update_data, expected_item',
        [
            (
                2,  # pit_in_id
                None,  # competition_id
                UpdatePitIn(  # update_data
                    lap=1,
                    pit_time=180000,
                    kart_status=KartStatus.UNKNOWN.value,
                    fixed_kart_status=None,
                ),
                {  # expected_item
                    'id': 2,
                    'competition_id': 2,
                    'team_id': 5,
                    'driver_id': 7,
                    'lap': 1,
                    'pit_time': 180000,
                    'kart_status': KartStatus.UNKNOWN.value,
                    'fixed_kart_status': None,
                    'has_pit_out': True,
                },
            ),
            (
                2,  # pit_in_id
                2,  # competition_id
                UpdatePitIn(  # update_data
                    lap=1,
                    pit_time=180000,
                    kart_status=KartStatus.UNKNOWN.value,
                    fixed_kart_status=None,
                ),
                {  # expected_item
                    'id': 2,
                    'competition_id': 2,
                    'team_id': 5,
                    'driver_id': 7,
                    'lap': 1,
                    'pit_time': 180000,
                    'kart_status': KartStatus.UNKNOWN.value,
                    'fixed_kart_status': None,
                    'has_pit_out': True,
                },
            ),
            (
                2,  # pit_in_id
                None,  # competition_id
                UpdatePitInDriver(  # update_data
                    driver_id=1,
                ),
                {  # expected_item
                    'id': 2,
                    'competition_id': 2,
                    'team_id': 5,
                    'driver_id': 1,
                    'lap': 1,
                    'pit_time': 151000,
                    'kart_status': KartStatus.UNKNOWN.value,
                    'fixed_kart_status': None,
                    'has_pit_out': True,
                },
            ),
            (
                2,  # pit_in_id
                None,  # competition_id
                UpdatePitInPitTime(  # update_data
                    pit_time=180000,
                ),
                {  # expected_item
                    'id': 2,
                    'competition_id': 2,
                    'team_id': 5,
                    'driver_id': 7,
                    'lap': 1,
                    'pit_time': 180000,
                    'kart_status': KartStatus.UNKNOWN.value,
                    'fixed_kart_status': None,
                    'has_pit_out': True,
                },
            ),
            (
                2,  # pit_in_id
                None,  # competition_id
                UpdatePitInKartStatus(  # update_data
                    kart_status=KartStatus.GOOD.value,
                ),
                {  # expected_item
                    'id': 2,
                    'competition_id': 2,
                    'team_id': 5,
                    'driver_id': 7,
                    'lap': 1,
                    'pit_time': 151000,
                    'kart_status': KartStatus.GOOD.value,
                    'fixed_kart_status': None,
                    'has_pit_out': True,
                },
            ),
            (
                2,  # pit_in_id
                None,  # competition_id
                UpdatePitInFixedKartStatus(  # update_data
                    fixed_kart_status=KartStatus.GOOD.value,
                ),
                {  # expected_item
                    'id': 2,
                    'competition_id': 2,
                    'team_id': 5,
                    'driver_id': 7,
                    'lap': 1,
                    'pit_time': 151000,
                    'kart_status': KartStatus.UNKNOWN.value,
                    'fixed_kart_status': KartStatus.GOOD.value,
                    'has_pit_out': True,
                },
            ),
        ])
    def test_update_by_id(
            self,
            pit_in_id: int,
            competition_id: Optional[int],
            update_data: TypeUpdatePitIn,
            expected_item: dict,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method update_by_id."""
        manager = PitsInManager(db=db_context, logger=fake_logger)

        before_item = manager.get_by_id(
            pit_in_id=pit_in_id, competition_id=competition_id)
        assert before_item is not None

        time.sleep(1)
        manager.update_by_id(
            update_data, pit_in_id=pit_in_id, competition_id=competition_id)

        after_item = manager.get_by_id(
            pit_in_id=pit_in_id, competition_id=competition_id)
        assert after_item is not None
        dict_item = after_item.model_dump(exclude=self.EXCLUDE)

        assert dict_item == expected_item
        assert before_item.insert_date == after_item.insert_date
        assert before_item.update_date < after_item.update_date


class TestPitsOutManager(DatabaseTest):
    """Test class ltsapi.managers.pits.PitsOutManager."""

    EXCLUDE = {
        'insert_date': True,
        'update_date': True,
    }

    @pytest.mark.parametrize(
        'competition_id, expected_items',
        [
            (
                2,  # competition_id
                [
                    {
                        'id': 1,
                        'competition_id': 2,
                        'team_id': 4,
                        'driver_id': 5,
                        'kart_status': KartStatus.UNKNOWN.value,
                        'fixed_kart_status': None,
                    },
                    {
                        'id': 2,
                        'competition_id': 2,
                        'team_id': 5,
                        'driver_id': 7,
                        'kart_status': KartStatus.UNKNOWN.value,
                        'fixed_kart_status': None,
                    },
                ],
            ),
        ])
    def test_get_by_competition_id(
            self,
            competition_id: int,
            expected_items: list,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method get_by_competition_id."""
        manager = PitsOutManager(db=db_context, logger=fake_logger)
        db_items = manager.get_by_competition_id(competition_id)
        dict_items = [x.model_dump(exclude=self.EXCLUDE) for x in db_items]
        assert dict_items == expected_items

    @pytest.mark.parametrize(
        'pit_out_id, competition_id, expected_item',
        [
            (
                1,  # pit_out_id
                None,  # competition_id
                {
                    'id': 1,
                    'competition_id': 2,
                    'team_id': 4,
                    'driver_id': 5,
                    'kart_status': KartStatus.UNKNOWN.value,
                    'fixed_kart_status': None,
                },
            ),
            (
                1,  # pit_out_id
                2,  # competition_id
                {
                    'id': 1,
                    'competition_id': 2,
                    'team_id': 4,
                    'driver_id': 5,
                    'kart_status': KartStatus.UNKNOWN.value,
                    'fixed_kart_status': None,
                },
            ),
        ])
    def test_get_by_id(
            self,
            pit_out_id: int,
            competition_id: Optional[int],
            expected_item: dict,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method get_by_id."""
        manager = PitsOutManager(db=db_context, logger=fake_logger)

        db_item = manager.get_by_id(
            pit_out_id=pit_out_id, competition_id=competition_id)
        assert db_item is not None

        dict_item = db_item.model_dump(exclude=self.EXCLUDE)
        assert dict_item == expected_item

    @pytest.mark.parametrize(
        'competition_id, team_id, expected_items',
        [
            (
                2,  # competition_id
                4,  # team_id
                [
                    {
                        'id': 1,
                        'competition_id': 2,
                        'team_id': 4,
                        'driver_id': 5,
                        'kart_status': KartStatus.UNKNOWN.value,
                        'fixed_kart_status': None,
                    },
                ],
            ),
        ])
    def test_get_by_team_id(
            self,
            competition_id: int,
            team_id: int,
            expected_items: list,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method get_by_team_id."""
        manager = PitsOutManager(db=db_context, logger=fake_logger)
        db_items = manager.get_by_team_id(competition_id, team_id)
        dict_items = [x.model_dump(exclude=self.EXCLUDE) for x in db_items]
        assert dict_items == expected_items

    @pytest.mark.parametrize(
        'competition_id, team_id, expected_item',
        [
            (
                2,  # competition_id
                5,  # team_id
                {  # expected_item
                    'id': 2,
                    'competition_id': 2,
                    'team_id': 5,
                    'driver_id': 7,
                    'kart_status': KartStatus.UNKNOWN.value,
                    'fixed_kart_status': None,
                },
            ),
        ])
    def test_get_last_by_team_id(
            self,
            competition_id: int,
            team_id: int,
            expected_item: dict,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method get_by_team_id."""
        manager = PitsOutManager(db=db_context, logger=fake_logger)
        db_item = manager.get_last_by_team_id(competition_id, team_id)
        assert db_item is not None

        dict_item = db_item.model_dump(exclude=self.EXCLUDE)
        assert dict_item == expected_item

    @pytest.mark.parametrize(
        'competition_id, model, expected_item',
        [
            (
                2,  # competition_id
                AddPitOut(
                    team_id=4,
                    driver_id=5,
                    kart_status=KartStatus.BAD,
                    fixed_kart_status=None,
                ),
                {
                    'id': None,
                    'competition_id': 2,
                    'team_id': 4,
                    'driver_id': 5,
                    'kart_status': KartStatus.BAD.value,
                    'fixed_kart_status': None,
                },
            ),
            (
                2,  # competition_id
                AddPitOut(
                    team_id=5,
                    driver_id=7,
                    kart_status=KartStatus.GOOD,
                    fixed_kart_status=None,
                ),
                {
                    'id': None,
                    'competition_id': 2,
                    'team_id': 5,
                    'driver_id': 7,
                    'kart_status': KartStatus.GOOD.value,
                    'fixed_kart_status': None,
                },
            ),
        ])
    def test_add_one(
            self,
            competition_id: Optional[int],
            model: AddPitOut,
            expected_item: dict,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method add_one."""
        manager = PitsOutManager(
            db=db_context,
            logger=fake_logger,
            pin_manager=PitsInManager(db=db_context, logger=fake_logger))
        item_id = manager.add_one(model, competition_id, commit=True)

        expected_item['id'] = item_id
        db_item = manager.get_by_id(item_id, competition_id)
        assert db_item is not None

        dict_item = db_item.model_dump(exclude=self.EXCLUDE)
        assert dict_item == expected_item

    @pytest.mark.parametrize(
        'pit_out_id, competition_id, update_data, expected_item',
        [
            (
                2,  # pit_out_id
                None,  # competition_id
                UpdatePitOut(  # update_data
                    kart_status=KartStatus.GOOD,
                    fixed_kart_status=None,
                ),
                {  # expected_item
                    'id': 2,
                    'competition_id': 2,
                    'team_id': 5,
                    'driver_id': 7,
                    'kart_status': KartStatus.GOOD.value,
                    'fixed_kart_status': None,
                },
            ),
            (
                2,  # pit_out_id
                None,  # competition_id
                UpdatePitOutDriver(  # update_data
                    driver_id=1,
                ),
                {  # expected_item
                    'id': 2,
                    'competition_id': 2,
                    'team_id': 5,
                    'driver_id': 1,
                    'kart_status': KartStatus.UNKNOWN.value,
                    'fixed_kart_status': None,
                },
            ),
            (
                2,  # pit_out_id
                None,  # competition_id
                UpdatePitOutKartStatus(  # update_data
                    kart_status=KartStatus.GOOD,
                ),
                {  # expected_item
                    'id': 2,
                    'competition_id': 2,
                    'team_id': 5,
                    'driver_id': 7,
                    'kart_status': KartStatus.GOOD.value,
                    'fixed_kart_status': None,
                },
            ),
            (
                2,  # pit_out_id
                None,  # competition_id
                UpdatePitOutFixedKartStatus(  # update_data
                    fixed_kart_status=KartStatus.GOOD,
                ),
                {  # expected_item
                    'id': 2,
                    'competition_id': 2,
                    'team_id': 5,
                    'driver_id': 7,
                    'kart_status': KartStatus.UNKNOWN.value,
                    'fixed_kart_status': KartStatus.GOOD.value,
                },
            ),
        ])
    def test_update_by_id(
            self,
            pit_out_id: int,
            competition_id: Optional[int],
            update_data: TypeUpdatePitOut,
            expected_item: dict,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method update_by_id."""
        manager = PitsOutManager(db=db_context, logger=fake_logger)

        before_item = manager.get_by_id(
            pit_out_id=pit_out_id, competition_id=competition_id)
        assert before_item is not None

        time.sleep(1)
        manager.update_by_id(
            update_data, pit_out_id=pit_out_id, competition_id=competition_id)

        after_item = manager.get_by_id(
            pit_out_id=pit_out_id, competition_id=competition_id)
        assert after_item is not None
        dict_item = after_item.model_dump(exclude=self.EXCLUDE)

        assert dict_item == expected_item
        assert before_item.insert_date == after_item.insert_date
        assert before_item.update_date < after_item.update_date


class TestPitsInOutManager(DatabaseTest):
    """
    Test class ltsapi.managers.pits.PitsInManager/PitsOutManager.
    """

    EXCLUDE = {
        'insert_date': True,
        'update_date': True,
    }

    @pytest.mark.parametrize(
        ('competition_id, team_id, model_pin, expected_pin,'
         'model_pout, expected_pout'),
        [
            (
                2,  # competition_id
                4,  # team_id
                AddPitIn(
                    team_id=4,
                    driver_id=5,
                    lap=10,
                    pit_time=None,
                    kart_status=KartStatus.GOOD,
                    fixed_kart_status=None,
                ),
                {
                    'id': None,
                    'competition_id': 2,
                    'team_id': 4,
                    'driver_id': 5,
                    'lap': 10,
                    'pit_time': None,
                    'kart_status': KartStatus.GOOD.value,
                    'fixed_kart_status': None,
                    'has_pit_out': False,
                },
                AddPitOut(
                    team_id=4,
                    driver_id=5,
                    kart_status=KartStatus.UNKNOWN,
                    fixed_kart_status=None,
                ),
                {
                    'id': None,
                    'competition_id': 2,
                    'team_id': 4,
                    'driver_id': 5,
                    'kart_status': KartStatus.UNKNOWN.value,
                    'fixed_kart_status': None,
                },
            ),
        ])
    def test_add_one(
            self,
            competition_id: Optional[int],
            team_id: int,
            model_pin: AddPitIn,
            expected_pin: dict,
            model_pout: AddPitOut,
            expected_pout: dict,
            db_context: DBContext,
            fake_logger: FakeLogger) -> None:
        """Test method add_one."""
        pin_manager = PitsInManager(db=db_context, logger=fake_logger)
        pout_manager = PitsOutManager(
            db=db_context, logger=fake_logger, pin_manager=pin_manager)

        # Insert pit-in
        item_id = pin_manager.add_one(model_pin, competition_id, commit=True)

        # Validate that the pit-in was inserted correctly
        expected_pin['id'] = item_id
        db_item = pin_manager.get_by_id(item_id, competition_id)
        assert db_item is not None

        dict_item = db_item.model_dump(exclude=self.EXCLUDE)
        assert dict_item == expected_pin

        # Insert pit-out
        item_id = pout_manager.add_one(model_pout, competition_id, commit=True)

        # Validate that the pit-out was inserted correctly
        expected_pout['id'] = item_id
        db_item = pout_manager.get_by_id(item_id, competition_id)
        assert db_item is not None

        dict_item = db_item.model_dump(exclude=self.EXCLUDE)
        assert dict_item == expected_pout

        # Validate that the pit-in has the flag 'has_pit_out' to true
        db_item = pin_manager.get_last_by_team_id(competition_id, team_id)
        assert db_item is not None

        dict_item = db_item.model_dump(exclude=self.EXCLUDE)
        expected_pin['has_pit_out'] = True
        assert dict_item == expected_pin

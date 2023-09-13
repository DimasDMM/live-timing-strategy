from fastapi import APIRouter, Path
from typing import Annotated, List, Union

from ltsapi import API_VERSION, _build_logger
from ltsapi.exceptions import ApiError
from ltsapi.managers.pits import (
    PitsInManager,
    PitsOutManager,
    TypeUpdatePitIn,
    TypeUpdatePitOut,
)
from ltsapi.models.pits import (
    AddPitIn,
    AddPitOut,
    GetPitIn,
    GetPitOut,
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
from ltsapi.models.responses import Empty
from ltsapi.router import _build_db_connection


router = APIRouter(
    prefix=f'/{API_VERSION}', tags=['Pits'])
_logger = _build_logger(__package__)


@router.get(
        path='/c/{competition_id}/pits/in',  # noqa: FS003
        summary='Get all the pits-in in a competition')
async def get_pits_in_by_competition(
    competition_id: Annotated[int, Path(description='ID of the competition')],
) -> List[GetPitIn]:
    """Get all the pits-in in a competition."""
    db = _build_db_connection(_logger)
    with db:
        manager = PitsInManager(db=db, logger=_logger)
        return manager.get_by_competition_id(competition_id)


@router.get(
        path='/c/{competition_id}/pits/in/{pit_in_id}',  # noqa: FS003
        summary='Get a pit-in by its ID')
async def get_pit_in_by_id(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    pit_in_id: Annotated[int, Path(description='ID of the pit-in')],
) -> Union[GetPitIn, Empty]:
    """Get a pit-in by its ID."""
    db = _build_db_connection(_logger)
    with db:
        manager = PitsInManager(db=db, logger=_logger)
        item = manager.get_by_id(pit_in_id, competition_id=competition_id)
        return Empty() if item is None else item


@router.put(
        path='/c/{competition_id}/pits/in/{pit_in_id}',  # noqa: FS003
        summary='Update a pit-in by its ID')
async def update_pit_in(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    pit_in_id: Annotated[int, Path(description='ID of the pit-in')],
    pit_in: UpdatePitIn,
) -> GetPitIn:
    """Update a pit-in by its ID."""
    return _update_pit_in_by_id(competition_id, pit_in_id, pit_in)


@router.put(
        path='/c/{competition_id}/pits/in/{pit_in_id}/driver',  # noqa: FS003
        summary='Update a pit-in (driver) by its ID')
async def update_pit_in_driver(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    pit_in_id: Annotated[int, Path(description='ID of the pit-in')],
    pit_in: UpdatePitInDriver,
) -> GetPitIn:
    """Update a pit-in (driver) by its ID."""
    return _update_pit_in_by_id(competition_id, pit_in_id, pit_in)


@router.put(
        path='/c/{competition_id}/pits/in/{pit_in_id}/pit_time',  # noqa: FS003
        summary='Update a pit-in (pit time) by its ID')
async def update_pit_in_pit_time(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    pit_in_id: Annotated[int, Path(description='ID of the pit-in')],
    pit_in: UpdatePitInPitTime,
) -> GetPitIn:
    """Update a pit-in (pit_time) by its ID."""
    return _update_pit_in_by_id(competition_id, pit_in_id, pit_in)


@router.put(
        path='/c/{competition_id}/pits/in/{pit_in_id}/kart_status',  # noqa
        summary='Update a pit-in (kart status) by its ID')
async def update_pit_in_kart_status(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    pit_in_id: Annotated[int, Path(description='ID of the pit-in')],
    pit_in: UpdatePitInKartStatus,
) -> GetPitIn:
    """Update a pit-in (kart status) by its ID."""
    return _update_pit_in_by_id(competition_id, pit_in_id, pit_in)


@router.put(
        path='/c/{competition_id}/pits/in/{pit_in_id}/fixed_kart_status',  # noqa
        summary='Update a pit-in (fixed kart status) by its ID')
async def update_pit_in_fixed_kart_status(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    pit_in_id: Annotated[int, Path(description='ID of the pit-in')],
    pit_in: UpdatePitInFixedKartStatus,
) -> GetPitIn:
    """Update a pit-in (fixed kart status) by its ID."""
    return _update_pit_in_by_id(competition_id, pit_in_id, pit_in)


def _update_pit_in_by_id(
        competition_id: int,
        pit_in_id: int,
        pit_in: TypeUpdatePitIn) -> GetPitIn:
    """Update a pit-in (any field) by its ID."""
    db = _build_db_connection(_logger)
    with db:
        db.start_transaction()
        manager = PitsInManager(db=db, logger=_logger)
        manager.update_by_id(
            pit_in, pit_in_id=pit_in_id, competition_id=competition_id)
        item = manager.get_by_id(pit_in_id, competition_id=competition_id)
        if item is None:
            raise ApiError('No data was inserted or updated.')
        return item


@router.post(
        path='/c/{competition_id}/pits/in',  # noqa: FS003
        summary='Add a new pit-in')
async def add_pit_in(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    pit_in: AddPitIn,
) -> GetPitIn:
    """Add a new pit-in."""
    db = _build_db_connection(_logger)
    with db:
        db.start_transaction()
        manager = PitsInManager(db=db, logger=_logger)
        try:
            item_id = manager.add_one(pit_in, competition_id, commit=True)
        except ApiError as e:
            raise e
        except Exception:
            raise ApiError('No data was inserted or updated.')
        item = manager.get_by_id(item_id, competition_id=competition_id)
        if item is None:
            raise ApiError('It was not possible to locate the new data.')
        return item


@router.get(
        path='/c/{competition_id}/pits/in/filter/team/{team_id}',  # noqa: FS003
        summary='Get the pits-in of a team')
async def get_pits_in_by_team(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    team_id: Annotated[int, Path(description='ID of the team')],
) -> List[GetPitIn]:
    """Get the pits-in of a team."""
    db = _build_db_connection(_logger)
    with db:
        manager = PitsInManager(db=db, logger=_logger)
        return manager.get_by_team_id(competition_id, team_id)


@router.get(
        path='/c/{competition_id}/pits/in/filter/team/{team_id}/last',  # noqa
        summary='Get the last pit-in of a team')
async def get_last_pit_in_by_team(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    team_id: Annotated[int, Path(description='ID of the team')],
) -> Union[GetPitIn, Empty]:
    """Get the last pit-in of a team."""
    db = _build_db_connection(_logger)
    with db:
        manager = PitsInManager(db=db, logger=_logger)
        item = manager.get_last_by_team_id(competition_id, team_id)
        return Empty() if item is None else item


@router.get(
        path='/c/{competition_id}/pits/out',  # noqa: FS003
        summary='Get all the pits-in in a competition')
async def get_pits_out_by_competition(
    competition_id: Annotated[int, Path(description='ID of the competition')],
) -> List[GetPitOut]:
    """Get all the pits-in in a competition."""
    db = _build_db_connection(_logger)
    with db:
        manager = PitsOutManager(db=db, logger=_logger)
        return manager.get_by_competition_id(competition_id)


@router.get(
        path='/c/{competition_id}/pits/out/{pit_out_id}',  # noqa: FS003
        summary='Get a pit-out by its ID')
async def get_pit_out_by_id(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    pit_out_id: Annotated[int, Path(description='ID of the pit-out')],
) -> Union[GetPitOut, Empty]:
    """Get a pit-out by its ID."""
    db = _build_db_connection(_logger)
    with db:
        manager = PitsOutManager(db=db, logger=_logger)
        item = manager.get_by_id(pit_out_id, competition_id=competition_id)
        return Empty() if item is None else item


@router.put(
        path='/c/{competition_id}/pits/out/{pit_out_id}',  # noqa: FS003
        summary='Update a pit-out by its ID')
async def update_pit_out(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    pit_out_id: Annotated[int, Path(description='ID of the pit-out')],
    pit_out: UpdatePitOut,
) -> GetPitOut:
    """Update a pit-out by its ID."""
    return _update_pit_out_by_id(competition_id, pit_out_id, pit_out)


@router.put(
        path='/c/{competition_id}/pits/out/{pit_out_id}/driver',  # noqa
        summary='Update a pit-out (driver) by its ID')
async def update_pit_out_driver(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    pit_out_id: Annotated[int, Path(description='ID of the pit-out')],
    pit_out: UpdatePitOutDriver,
) -> GetPitOut:
    """Update a pit-out (driver) by its ID."""
    return _update_pit_out_by_id(competition_id, pit_out_id, pit_out)


@router.put(
        path='/c/{competition_id}/pits/out/{pit_out_id}/kart_status',  # noqa
        summary='Update a pit-out (kart status) by its ID')
async def update_pit_out_kart_status(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    pit_out_id: Annotated[int, Path(description='ID of the pit-out')],
    pit_out: UpdatePitOutKartStatus,
) -> GetPitOut:
    """Update a pit-out (kart status) by its ID."""
    return _update_pit_out_by_id(competition_id, pit_out_id, pit_out)


@router.put(
        path='/c/{competition_id}/pits/out/{pit_out_id}/fixed_kart_status',  # noqa
        summary='Update a pit-out (fixed kart status) by its ID')
async def update_pit_out_fixed_kart_status(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    pit_out_id: Annotated[int, Path(description='ID of the pit-out')],
    pit_out: UpdatePitOutFixedKartStatus,
) -> GetPitOut:
    """Update a pit-out (fixed kart status) by its ID."""
    return _update_pit_out_by_id(competition_id, pit_out_id, pit_out)


def _update_pit_out_by_id(
        competition_id: int,
        pit_out_id: int,
        pit_out: TypeUpdatePitOut) -> GetPitOut:
    """Update a pit-out (any field) by its ID."""
    db = _build_db_connection(_logger)
    with db:
        db.start_transaction()
        manager = PitsOutManager(db=db, logger=_logger)
        manager.update_by_id(
            pit_out, pit_out_id=pit_out_id, competition_id=competition_id)
        item = manager.get_by_id(pit_out_id, competition_id=competition_id)
        if item is None:
            raise ApiError('No data was inserted or updated.')
        return item


@router.post(
        path='/c/{competition_id}/pits/out',  # noqa: FS003
        summary='Add a new pit-out')
async def add_pit_out(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    pit_out: AddPitOut,
) -> GetPitOut:
    """Add a new pit-out."""
    db = _build_db_connection(_logger)
    with db:
        db.start_transaction()
        manager = PitsOutManager(
            db=db,
            logger=_logger,
            pin_manager=PitsInManager(db=db, logger=_logger))
        try:
            item_id = manager.add_one(pit_out, competition_id, commit=True)
        except ApiError as e:
            raise e
        except Exception:
            raise ApiError('No data was inserted or updated.')
        item = manager.get_by_id(item_id, competition_id=competition_id)
        if item is None:
            raise ApiError('It was not possible to locate the new data.')
        return item


@router.get(
        path='/c/{competition_id}/pits/out/filter/team/{team_id}',  # noqa
        summary='Get the pits-in of a team')
async def get_pits_out_by_team(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    team_id: Annotated[int, Path(description='ID of the team')],
) -> List[GetPitOut]:
    """Get the pits-in of a team."""
    db = _build_db_connection(_logger)
    with db:
        manager = PitsOutManager(db=db, logger=_logger)
        return manager.get_by_team_id(competition_id, team_id)


@router.get(
        path='/c/{competition_id}/pits/out/filter/team/{team_id}/last',  # noqa
        summary='Get the last pit-out of a team')
async def get_last_pit_out_by_team(
    competition_id: Annotated[int, Path(description='ID of the competition')],
    team_id: Annotated[int, Path(description='ID of the team')],
) -> Union[GetPitOut, Empty]:
    """Get the last pit-out of a team."""
    db = _build_db_connection(_logger)
    with db:
        manager = PitsOutManager(db=db, logger=_logger)
        item = manager.get_last_by_team_id(competition_id, team_id)
        return Empty() if item is None else item

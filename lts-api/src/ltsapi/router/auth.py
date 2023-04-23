from fastapi import APIRouter

from ltsapi import API_VERSION, _build_logger
from ltsapi.exceptions import ApiError
from ltsapi.managers.auth import AuthManager
from ltsapi.models.health import GetHealth
from ltsapi.models.auth import (
    GetAuth,
    SendAuthKey,
)
from ltsapi.router import _build_db_connection


router = APIRouter(
    prefix='/' + API_VERSION,  # noqa
    tags=['Auth and health'])
_logger = _build_logger(__package__)


@router.get(
        path='/health',
        summary='Get API status')
async def get_health() -> GetHealth:
    """Get API health."""
    return GetHealth(status='ok')


@router.post(
        path='/auth',  # noqa: FS003
        summary='Do authentication in the API REST')
async def do_auth(auth_key: SendAuthKey) -> GetAuth:
    """Do authentication in the API REST."""
    db = _build_db_connection(_logger)
    with db:
        manager = AuthManager(db=db, logger=_logger)
        item = manager.refresh_bearer(auth_key.key, commit=True)
        if item is None:
            raise ApiError()
        else:
            return item

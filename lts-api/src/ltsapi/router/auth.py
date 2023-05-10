from fastapi import APIRouter, Header
import re
from typing import Annotated, Optional, Union

from ltsapi import API_VERSION, _build_logger
from ltsapi.exceptions import ApiError
from ltsapi.managers.auth import AuthManager
from ltsapi.models.health import GetHealth
from ltsapi.models.auth import (
    GetAuth,
    SendAuthKey,
    ValidateAuth,
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
        db.start_transaction()
        manager = AuthManager(db=db, logger=_logger)
        item = manager.refresh_bearer(auth_key.key, commit=True)
        if item is None:
            raise ApiError('An error occured with the bearer token.')
        else:
            return item


@router.get(
        path='/auth/validate',  # noqa: FS003
        summary='Validate Bearer token')
async def validate_auth(
    authorization: Annotated[Optional[str], Header(alias='Authorization')],
) -> ValidateAuth:
    """Do authentication in the API REST."""
    db = _build_db_connection(_logger)
    with db:
        manager = AuthManager(db=db, logger=_logger)
        item = manager.get_by_bearer(authorization)
        if item is None:
            raise ApiError(
                message='Invalid authentication.',
                status_code=403,
            )
        return item

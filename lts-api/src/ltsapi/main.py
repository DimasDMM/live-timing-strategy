from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import json
import os
import traceback
from typing import Callable

from ltsapi import _build_logger
from ltsapi.exceptions import ApiError
from ltsapi.managers.auth import AuthManager
from ltsapi.models.responses import ErrorResponse
from ltsapi.router import _build_db_connection
from ltsapi.router.auth import router as router_auth
from ltsapi.router.competitions import router as router_competitions
from ltsapi.router.misc import router as router_misc
from ltsapi.router.participants import router as router_participants
from ltsapi.router.pits import router as router_pits
from ltsapi.router.timing import router as router_timing

# Name of the header that contains the auth token
HEADER_BEARER = 'Authorization'

# Endpoints that do not require authentication
NON_AUTH_ENDPOINTS = [
    '/docs',
    '/openapi.json',
    '/v1/health',
    '/v1/auth',
]

# Init logger
_logger = _build_logger(__package__)
_ = _build_db_connection(_logger)

# Init API REST
app = FastAPI(
    title='Live Timing Strategy',
    description='OpenAPI schema of LTS application',
    version='0.0.1',
)


@app.exception_handler(ApiError)
async def api_error_handler(
        request: Request, exc: ApiError) -> JSONResponse:  # noqa: U100
    """Handle and display error messages."""
    return JSONResponse(
        status_code=exc.get_status_code(),
        content=exc.to_error_response().dict(),
    )


@app.exception_handler(Exception)
async def debug_exception_handler(
        request: Request, exc: Exception) -> JSONResponse:  # noqa: U100
    """Display exception traceback for debug purposes."""
    if os.environ.get('DEBUG', default=False):
        content = ''.join(
            traceback.format_exception(
                type(exc),
                value=exc,
                tb=exc.__traceback__,
            ),
        )
    else:
        content = 'An error occured.'
    return JSONResponse(
        status_code=500,
        content=content,
    )


@app.middleware('http')
async def auth_middleware(request: Request, call_next: Callable) -> Response:
    """Validate auth data."""
    url = request.url

    # Excluded endpoints from authentication
    for non_auth in NON_AUTH_ENDPOINTS:
        if url.path.startswith(non_auth):
            response = await call_next(request)
            return response

    try:
        # Validate bearer token
        db = _build_db_connection(_logger)
        with db:
            manager = AuthManager(db=db, logger=_logger)
            bearer = request.headers.get(HEADER_BEARER, None)
            if bearer is None:
                return _build_response_403()

            auth = manager.get_by_bearer(bearer=bearer)
            if auth is None:
                return _build_response_403()

        # Forward response if bearer token was valid
        response: Response = await call_next(request)  # type: ignore
        return response
    except Exception as e:
        if isinstance(e, ApiError):
            error = e.to_error_response()
        else:
            error = ErrorResponse(
                message='An error has occured.',
                status_code=500,
                extra_data={
                    'exception': str(e),
                    'traceback': str(e.__traceback__),
                },
            )
        return JSONResponse(content=error.dict(), status_code=error.status_code)


def _build_response_403() -> Response:
    """Return 403 response."""
    content = ErrorResponse(message='Invalid authentication.', status_code=403)
    return Response(
        status_code=403,
        content=json.dumps(content.dict()),
    )


app.include_router(router_auth)
app.include_router(router_competitions)
app.include_router(router_misc)
app.include_router(router_participants)
app.include_router(router_pits)
app.include_router(router_timing)

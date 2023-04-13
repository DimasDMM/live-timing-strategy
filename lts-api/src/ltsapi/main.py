from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os
import traceback

from ltsapi.exceptions import ApiError
from ltsapi.router.competitions import router as router_competitions
from ltsapi.router.participants import router as router_participants
from ltsapi.router.timing import router as router_timing


app = FastAPI(
    title='Live Timing Strategy',
    description='OpenAPI schema of LTS application',
    version='0.0.1',
)
app.include_router(router_competitions)
app.include_router(router_participants)
app.include_router(router_timing)


@app.exception_handler(ApiError)
async def api_error_handler(
        request: Request, exc: ApiError) -> JSONResponse:  # noqa: U100
    """Handle and display error messages."""
    return JSONResponse(
        status_code=exc.get_status_code(),
        content=exc.error_response().dict(),
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

from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from starlette import status
from fastapi.responses import JSONResponse
from loguru import logger

async def global_exception_handler(request: Request, exc: Exception):
    """Handles uncaught exception globally."""
    logger.error(f"Uncaught Error: {repr(exc)}, Path: {request.url}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occured."}
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    """Handles FASTApi HTTP Exceptions."""
    logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail}, Path: {request.url}")

    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation Error: {exc.errors()} | Path: {request.url}")

    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )
from http import HTTPStatus

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.g import request_id_var
from config import settings
from logger import logger
from utility.base_exceptions import BaseHTTPError


def error_response(
    status_code: int, code: str, message: str, details: object = None
) -> JSONResponse:
    error = {"code": code, "message": message, "request_id": request_id_var.get()}
    if details is not None:
        error["details"] = details
    return JSONResponse(status_code=status_code, content={"error": error})


async def handle_base_http_error(request: Request, exc: BaseHTTPError) -> JSONResponse:
    if exc.status_code >= HTTPStatus.INTERNAL_SERVER_ERROR:
        logger.error("request failed", exc_info=exc)
        message = exc.message if settings.EXPOSE_ERROR_DETAILS else exc.default_message
    else:
        logger.warning("request rejected", extra={"fields": {"code": exc.code}})
        message = exc.message
    return error_response(exc.status_code, exc.code, message)


async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    return error_response(
        HTTPStatus.UNPROCESSABLE_ENTITY,
        "VALIDATION_ERROR",
        "The request failed validation.",
        details=jsonable_encoder(exc.errors()),
    )


async def handle_http_exception(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    status = HTTPStatus(exc.status_code)
    message = str(exc.detail) if status < HTTPStatus.INTERNAL_SERVER_ERROR else status.phrase
    return error_response(status, status.name, message)


def handle_unexpected_error(exc: Exception) -> JSONResponse:
    logger.error("unhandled exception", exc_info=exc)
    message = (
        f"{type(exc).__name__}: {exc}"
        if settings.EXPOSE_ERROR_DETAILS
        else BaseHTTPError.default_message
    )
    return error_response(HTTPStatus.INTERNAL_SERVER_ERROR, BaseHTTPError.code, message)

import re
import time
from uuid import uuid4

from fastapi import Request, Response

from app.exception_handlers import handle_unexpected_error
from app.g import request_id_var
from config import settings
from logger import logger
from utility.metrics import REQUEST_LATENCY

REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
QUIET_PATHS = {"/healthCheck", "/metrics"}
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
}
HSTS_HEADER = "max-age=31536000; includeSubDomains"


def resolve_request_id(incoming: str | None) -> str:
    if incoming and REQUEST_ID_PATTERN.match(incoming):
        return incoming
    return uuid4().hex


async def request_context_middleware(request: Request, call_next) -> Response:
    request_id = resolve_request_id(request.headers.get("X-Request-ID"))
    token = request_id_var.set(request_id)
    start = time.perf_counter()
    try:
        try:
            response = await call_next(request)
        except Exception as exc:
            response = handle_unexpected_error(exc)

        duration = time.perf_counter() - start
        route = getattr(request.scope.get("route"), "path", "unmatched")
        REQUEST_LATENCY.labels(request.method, route, response.status_code).observe(duration)
        response.headers["X-Request-ID"] = request_id
        response.headers.update(SECURITY_HEADERS)
        if settings.ENABLE_HSTS:
            response.headers["Strict-Transport-Security"] = HSTS_HEADER

        if request.url.path not in QUIET_PATHS:
            logger.info(
                "request finished",
                extra={
                    "fields": {
                        "method": request.method,
                        "path": request.url.path,
                        "status": response.status_code,
                        "duration_ms": round(duration * 1000, 1),
                    }
                },
            )
        return response
    finally:
        request_id_var.reset(token)

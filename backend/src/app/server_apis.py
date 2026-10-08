import asyncio
from collections.abc import Awaitable, Callable

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from config import settings
from logger import logger

PING_TIMEOUT_SECONDS = 2

server_router = APIRouter()


async def check_dependency(name: str, ping: Callable[[], Awaitable[object]]) -> str:
    try:
        await asyncio.wait_for(ping(), timeout=PING_TIMEOUT_SECONDS)
        return "ok"
    except Exception as exc:
        logger.warning(
            "dependency check failed", extra={"fields": {"dependency": name}}, exc_info=exc
        )
        return "down"


@server_router.get("/healthCheck")
async def health_check(request: Request) -> JSONResponse:
    state = request.app.state
    checks = {
        "mongo": await check_dependency("mongo", lambda: state.mongo.admin.command("ping")),
        "redis": await check_dependency("redis", state.redis.ping),
    }
    healthy = all(result == "ok" for result in checks.values())
    return JSONResponse(
        status_code=200 if healthy else 503,
        content={
            "status": "ok" if healthy else "degraded",
            "version": settings.VERSION,
            "checks": checks,
        },
    )


@server_router.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

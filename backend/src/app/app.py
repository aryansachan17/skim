from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pymongo import AsyncMongoClient
from redis.asyncio import Redis
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.exception_handlers import (
    handle_base_http_error,
    handle_http_exception,
    handle_validation_error,
)
from app.graphql_schema import get_graphql_router
from app.middlewares import request_context_middleware
from app.server_apis import server_router
from config import settings
from logger import logger, setup_logging
from utility.base_exceptions import BaseHTTPError


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    mongo = AsyncMongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=2000)
    redis = Redis.from_url(settings.REDIS_URL, socket_timeout=2, socket_connect_timeout=2)
    app.state.mongo = mongo
    app.state.db = mongo[settings.MONGO_DB]
    app.state.redis = redis
    logger.info("skim api started", extra={"fields": {"env": settings.current_env.lower()}})
    try:
        yield
    finally:
        await redis.aclose()
        await mongo.close()


def get_skim_app() -> FastAPI:
    setup_logging(settings.LOG_LEVEL)
    app = FastAPI(title="Skim API", lifespan=lifespan, docs_url=None, redoc_url=None)

    app.middleware("http")(request_context_middleware)
    if settings.CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ORIGINS,
            allow_methods=["GET", "POST"],
            allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
            expose_headers=["X-Request-ID"],
        )

    app.add_exception_handler(BaseHTTPError, handle_base_http_error)
    app.add_exception_handler(RequestValidationError, handle_validation_error)
    app.add_exception_handler(StarletteHTTPException, handle_http_exception)

    app.include_router(server_router)
    app.include_router(get_graphql_router(), prefix="/graphql")
    return app

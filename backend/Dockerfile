# syntax=docker/dockerfile:1

FROM python:3.12-slim AS build
COPY --from=ghcr.io/astral-sh/uv:0.12.23 /uv /usr/local/bin/uv
ENV UV_NO_CONFIG=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project
COPY settings.toml ./
COPY src ./src

FROM python:3.12-slim
RUN useradd --create-home --uid 10001 skim
WORKDIR /app
COPY --from=build /app /app
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    SKIM_ENV=production
USER skim
EXPOSE 8000
CMD ["python", "src/server.py"]

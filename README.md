# Skim

**Save anything, understand it in 30 seconds, find it later.**

Skim is a read-it-later app: save a link, a background worker fetches the article, an open-source language model summarizes and tags it, and you can search your library by keyword, tag or meaning. It's a learning project, built to practise backend and frontend engineering end to end.

> Status: in development. Today it has the API and web skeletons, CI and image publishing; features land day by day.

## Stack

| Part | Technology |
|---|---|
| API | Python 3.12, FastAPI, Strawberry GraphQL, async PyMongo, Redis |
| Web | React, TypeScript, Vite, Apollo Client, GraphQL Code Generator |
| Tooling | uv, pnpm (via Corepack), Ruff, pytest, Vitest |
| Delivery | GitHub Actions, Docker, GitHub Container Registry |

## Run it locally

You need `uv`, Node 24 (with Corepack), MongoDB and Redis running locally.

```bash
make install          # backend dependencies
make web-install      # frontend dependencies
make run-api          # API on http://127.0.0.1:8000
make run-web          # web app on http://localhost:5173 (proxies /graphql to the API)
```

The Makefile expects Node 24 at `/opt/homebrew/opt/node@24/bin`; override it with `make NODE24=/path/to/node24/bin run-web`.

## Everyday commands

| Command | What it does |
|---|---|
| `make test` | backend tests with an 80% coverage gate |
| `make lint` / `make format` | check / fix backend style |
| `make web-test` | frontend tests |
| `make web-build` | type check and build the frontend |
| `make codegen` | export the GraphQL schema and regenerate typed hooks |
| `make check-registry` | confirm both lockfiles use public registries only |

## How changes ship

`main` is protected: changes arrive through pull requests, and every PR must pass CI (leak guard, commit-message check, backend lint and tests, frontend type check, build and tests, GraphQL contract checks, and a Docker build with a boot test). After a merge, the backend image is published as `ghcr.io/aryansachan17/skim-backend:main-<sha>`. Hosting is paused for now; see [docs/deployment.md](docs/deployment.md).

## Layout

```
backend/    FastAPI app (src/), tests, settings per environment, Dockerfile
frontend/   React app, GraphQL schema and generated hooks
docs/       deployment notes
.github/    CI and image publishing workflows
```

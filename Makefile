# uv must ignore machine-wide config so packages only come from public PyPI.
export UV_NO_CONFIG := 1
BACKEND := backend
FRONTEND := frontend

# The frontend uses Node 24 without changing the shell's default Node version.
NODE24 ?= /opt/homebrew/opt/node@24/bin
PNPM = cd $(FRONTEND) && PATH="$(NODE24):$$PATH" COREPACK_ENABLE_DOWNLOAD_PROMPT=0 corepack pnpm

.PHONY: install run-api test lint format schema web-install run-web web-test web-typecheck web-build codegen check-registry

install:
	cd $(BACKEND) && uv sync

run-api:
	cd $(BACKEND) && uv run python src/server.py

test:
	cd $(BACKEND) && uv run pytest --cov --cov-report=term-missing --cov-fail-under=80

lint:
	cd $(BACKEND) && uv run ruff check . && uv run ruff format --check .

format:
	cd $(BACKEND) && uv run ruff format . && uv run ruff check --fix .

schema:
	cd $(BACKEND) && PYTHONPATH=src uv run python scripts/export_schema.py ../$(FRONTEND)/schema.graphql

web-install:
	$(PNPM) install

run-web:
	$(PNPM) dev

web-test:
	$(PNPM) test

web-typecheck:
	$(PNPM) typecheck

web-build:
	$(PNPM) build

codegen: schema
	$(PNPM) codegen

check-registry:
	@hosts=$$(grep -ohE 'https://[^/"]+' $(BACKEND)/uv.lock $(FRONTEND)/pnpm-lock.yaml 2>/dev/null | sort -u \
	  | grep -vE '^https://(pypi\.org|files\.pythonhosted\.org|registry\.npmjs\.org)$$'); \
	if [ -n "$$hosts" ]; then echo "Non-public package registry in a lockfile: $$hosts"; exit 1; fi; \
	echo "Lockfiles use public registries only"

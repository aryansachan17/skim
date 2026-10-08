# uv must ignore machine-wide config so packages only come from public PyPI.
export UV_NO_CONFIG := 1
BACKEND := backend

.PHONY: install run-api test lint format check-registry

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

check-registry:
	@hosts=$$(grep -oE 'https://[^/"]+' $(BACKEND)/uv.lock | sort -u | grep -vE '^https://(pypi\.org|files\.pythonhosted\.org)$$'); \
	if [ -n "$$hosts" ]; then echo "Non-public package registry in uv.lock: $$hosts"; exit 1; fi; \
	echo "uv.lock uses public PyPI only"

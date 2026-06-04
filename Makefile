.PHONY: dev down reset verify ci verify-release-artifacts logs test-api test-web build-web smoke e2e-local

dev:
	docker compose up --build

down:
	docker compose down

reset:
	./scripts/reset-lab.sh
# Dynamic discovery of bun executable
BUN := $(shell which bun 2>/dev/null || ( [ -f ~/.bun/bin/bun ] && echo ~/.bun/bin/bun ) || echo "NOT_FOUND")

verify:
	@if [ "$(BUN)" = "NOT_FOUND" ]; then \
		echo "Error: 'bun' not found in PATH or ~/.bun/bin/bun."; \
		echo "Please install bun or set BUN_PATH environment variable."; \
		exit 1; \
	fi
	./scripts/verify-local-only.sh
	./scripts/validate-mission-authoring.py
	./scripts/verify-release-artifacts.sh
	cd apps/api && AWS_ENDPOINT_URL=http://floci:4566 AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test AWS_DEFAULT_REGION=us-east-1 uv run pytest
	cd apps/api && AWS_ENDPOINT_URL=http://floci:4566 AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test AWS_DEFAULT_REGION=us-east-1 uv run ruff check app tests
	cd apps/web && $(BUN) install && $(BUN) run typecheck
	cd apps/web && NEXT_TELEMETRY_DISABLED=1 $(BUN) run build
	docker compose down --remove-orphans
	docker compose run --rm api rm -f /app/data/verify_test.db
	API_PORT=18000 WEB_PORT=13000 FLOCI_PORT=14566 NEXT_PUBLIC_API_URL=http://localhost:18000 DATABASE_URL=sqlite:////app/data/verify_test.db docker compose up --build -d
	API_URL=http://localhost:18000 WEB_URL=http://localhost:13000 FLOCI_URL=http://localhost:14566 ./scripts/smoke-test.sh
	API_URL=http://localhost:18000 FLOCI_URL=http://localhost:14566 ./scripts/e2e-local-flow.py
	API_PORT=18000 WEB_PORT=13000 FLOCI_PORT=14566 NEXT_PUBLIC_API_URL=http://localhost:18000 docker compose down


logs:
	docker compose logs -f

test-api:
	cd apps/api && uv run pytest

test-web:
	cd apps/web && bun run typecheck

build-web:
	cd apps/web && bun run build

smoke:
	./scripts/smoke-test.sh

e2e-local:
	./scripts/e2e-local-flow.py

verify-release-artifacts:
	./scripts/verify-release-artifacts.sh

# ci: run the same checks as the GitHub Actions workflow, entirely locally.
# Requires: uv, bun, ripgrep. Does NOT need Docker or GitHub minutes.
ci:
	./scripts/verify-local-only.sh
	cd apps/api && AWS_ENDPOINT_URL=http://localhost:4566 uv run pytest -v
	cd apps/web && bun install --frozen-lockfile
	cd apps/web && NEXT_TELEMETRY_DISABLED=1 bun run build

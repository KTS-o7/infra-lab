.PHONY: dev down reset verify logs test-api test-web build-web smoke

dev:
	docker compose up --build

down:
	docker compose down

reset:
	./scripts/reset-lab.sh

verify:
	./scripts/verify-local-only.sh
	cd apps/api && uv run pytest
	docker compose up --build
	./scripts/smoke-test.sh

logs:
	docker compose logs -f

test-api:
	cd apps/api && uv run pytest

test-web:
	bun --cwd apps/web test

build-web:
	bun --cwd apps/web run build

smoke:
	./scripts/smoke-test.sh
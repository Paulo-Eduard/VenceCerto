up:
	docker compose up --build
test-backend:
	cd backend && python -m pytest -q
lint:
	cd backend && ruff check .

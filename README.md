# Incident Router

A small FastAPI service that routes operational incident messages to an owning team.

## Setup

```powershell
uv sync --dev
```

## Run

```powershell
uv run uvicorn app.main:app --reload
```

## Test

```powershell
uv run python -m pytest -q
```

## Endpoints

- `GET /health`
- `POST /route`

The starter implementation uses a deterministic local router so the project can run without external credentials.

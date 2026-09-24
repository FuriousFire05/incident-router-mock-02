# Incident Router

A small FastAPI service that deterministically routes operational incident messages to an owning team and severity.

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

- `GET /health` — returns `{"status": "healthy"}`.
- `POST /route` — routes one incident.
- `POST /route/batch` — routes a batch of incidents.
- `GET /stats` — returns process-local routing counters.

## Route an incident

`POST /route`

```json
{
  "message": "My withdrawal is missing",
  "customer_tier": "standard",
  "source": "web"
}
```

- `message` is required, trimmed, and must be non-empty. Its maximum length is 1,000 characters.
- `customer_tier` defaults to `standard` and accepts `standard` or `vip`.
- `source` is optional and accepts `web`, `mobile`, or `api`.
- Unexpected request fields are rejected with HTTP 422.
- The existing deterministic keyword and category routing is applied first.
- Messages containing `hacked`, `fraud`, or `compromised` are globally assigned critical severity.
- A VIP result that would otherwise have medium severity is escalated to high.
- VIP escalation never downgrades or replaces a critical result.

Example response:

```json
{
  "team": "payments",
  "severity": "medium",
  "reason": "Message mentions a payments-related issue.",
  "confidence": 0.82
}
```

## Route a batch

`POST /route/batch`

```json
{
  "items": [
    {"message": "My withdrawal is delayed"},
    {"message": "The mobile app crashed", "source": "mobile"}
  ]
}
```

A batch must contain 1–20 items. Every item uses the same validation and routing behavior as `POST /route`, and results preserve input order. Unexpected outer or item fields are rejected.

Response shape:

```json
{
  "results": [
    {
      "team": "payments",
      "severity": "medium",
      "reason": "Message mentions a payments-related issue.",
      "confidence": 0.82
    }
  ]
}
```

## Statistics

`GET /stats`

```json
{
  "route_requests": 0,
  "batch_requests": 0,
  "items_routed": 0,
  "critical_results": 0
}
```

- `route_requests` counts successful `POST /route` requests.
- `batch_requests` counts successful `POST /route/batch` requests.
- `items_routed` counts successfully routed individual items across both endpoints.
- `critical_results` counts returned results with critical severity.
- Requests rejected with HTTP 422 do not increment any counter.

## Design

Routing rules and deterministic routing behavior live in `app/router.py`. API endpoints and validation/response models live in `app/main.py` and `app/models.py`. Counters are held in process memory on the FastAPI application state, with updates and snapshots protected by a lock.

## Limitations

Counters reset whenever the process restarts. Each server process or worker maintains its own independent counters, and there is no persistent or global aggregation.

from threading import Lock

from fastapi import FastAPI

from app.models import (
    BatchRouteRequest,
    BatchRouteResult,
    RouteRequest,
    RouteResult,
    StatsResult,
)
from app.router import route_message


class CounterStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self.reset()

    def reset(self) -> None:
        with self._lock:
            self._route_requests = 0
            self._batch_requests = 0
            self._items_routed = 0
            self._critical_results = 0

    def record_route(self, result: RouteResult) -> None:
        with self._lock:
            self._route_requests += 1
            self._items_routed += 1
            self._critical_results += result.severity == "critical"

    def record_batch(self, results: list[RouteResult]) -> None:
        with self._lock:
            self._batch_requests += 1
            self._items_routed += len(results)
            self._critical_results += sum(
                result.severity == "critical" for result in results
            )

    def snapshot(self) -> StatsResult:
        with self._lock:
            return StatsResult(
                route_requests=self._route_requests,
                batch_requests=self._batch_requests,
                items_routed=self._items_routed,
                critical_results=self._critical_results,
            )


app = FastAPI(title="Incident Router")
app.state.counters = CounterStore()

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}

@app.post("/route", response_model=RouteResult)
def route(request: RouteRequest) -> RouteResult:
    result = route_message(request.message, request.customer_tier)
    app.state.counters.record_route(result)
    return result

@app.post("/route/batch", response_model=BatchRouteResult)
def route_batch(request: BatchRouteRequest) -> BatchRouteResult:
    results = [
        route_message(item.message, item.customer_tier) for item in request.items
    ]
    app.state.counters.record_batch(results)
    return BatchRouteResult(results=results)

@app.get("/stats", response_model=StatsResult)
def stats() -> StatsResult:
    return app.state.counters.snapshot()

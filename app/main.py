from fastapi import FastAPI

from app.models import RouteRequest, RouteResult
from app.router import route_message

app = FastAPI(title="Incident Router")

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}

@app.post("/route", response_model=RouteResult)
def route(request: RouteRequest) -> RouteResult:
    return route_message(request.message)

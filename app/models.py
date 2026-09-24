from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing_extensions import Annotated

Message = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1000)]
CustomerTier = Literal["standard", "vip"]
Source = Literal["web", "mobile", "api"]

class RouteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    message: Message
    customer_tier: CustomerTier = "standard"
    source: Source | None = None

class RouteResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    team: Literal["payments", "accounts", "trading", "platform", "general"]
    severity: Literal["low", "medium", "high", "critical"]
    reason: Message
    confidence: float = Field(ge=0.0, le=1.0)

class BatchRouteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    items: list[RouteRequest] = Field(min_length=1, max_length=20)

class BatchRouteResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    results: list[RouteResult]

class StatsResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    route_requests: int = Field(ge=0)
    batch_requests: int = Field(ge=0)
    items_routed: int = Field(ge=0)
    critical_results: int = Field(ge=0)

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing_extensions import Annotated

Message = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1000)]

class RouteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    message: Message

class RouteResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    team: Literal["payments", "accounts", "trading", "platform", "general"]
    severity: Literal["low", "medium", "high", "critical"]
    reason: Message
    confidence: float = Field(ge=0.0, le=1.0)

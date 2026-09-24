from dataclasses import dataclass

from app.models import CustomerTier, RouteResult

@dataclass(frozen=True)
class Rule:
    keywords: tuple[str, ...]
    team: str
    severity: str
    reason: str
    confidence: float

RULES = (
    Rule(("withdrawal", "deposit", "card", "payment"), "payments", "medium",
         "Message mentions a payments-related issue.", 0.82),
    Rule(("password", "login", "account", "verification"), "accounts", "medium",
         "Message mentions an account-access issue.", 0.80),
    Rule(("order", "position", "trade", "price"), "trading", "medium",
         "Message mentions a trading issue.", 0.78),
    Rule(("app", "website", "api", "connection", "crash"), "platform", "medium",
         "Message mentions a platform issue.", 0.76),
)

CRITICAL_KEYWORDS = ("hacked", "stolen", "fraud", "compromised")
GLOBAL_CRITICAL_KEYWORDS = ("hacked", "fraud", "compromised")
HIGH_KEYWORDS = ("blocked", "cannot access", "can't access", "missing money")

def route_message(message: str, customer_tier: CustomerTier = "standard") -> RouteResult:
    normalized = " ".join(message.lower().split())

    result = _route_by_keyword(normalized)

    if any(keyword in normalized for keyword in GLOBAL_CRITICAL_KEYWORDS):
        return result.model_copy(update={"severity": "critical"})
    if customer_tier == "vip" and result.severity == "medium":
        return result.model_copy(update={"severity": "high"})
    return result

def _route_by_keyword(normalized: str) -> RouteResult:
    for rule in RULES:
        if any(keyword in normalized for keyword in rule.keywords):
            severity = rule.severity
            if any(keyword in normalized for keyword in CRITICAL_KEYWORDS):
                severity = "critical"
            elif any(keyword in normalized for keyword in HIGH_KEYWORDS):
                severity = "high"

            return RouteResult(
                team=rule.team,
                severity=severity,
                reason=rule.reason,
                confidence=rule.confidence,
            )

    return RouteResult(
        team="general",
        severity="low",
        reason="No specialized routing rule matched.",
        confidence=0.55,
    )

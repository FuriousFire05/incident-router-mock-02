from app.router import route_message

def test_account_routing():
    result = route_message("I cannot login to my account")
    assert result.team == "accounts"
    assert result.severity == "medium"

def test_critical_keyword_escalates_matching_rule():
    result = route_message("My card was stolen and I think funds are compromised")
    assert result.team == "payments"
    assert result.severity == "critical"

def test_unknown_message_goes_to_general():
    result = route_message("I have a question about something unrelated")
    assert result.team == "general"
    assert result.severity == "low"

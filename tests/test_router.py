from app.router import route_message

def test_account_routing():
    result = route_message("I cannot login to my account")
    assert result.team == "accounts"
    assert result.severity == "medium"

def test_critical_keyword_escalates_matching_rule():
    result = route_message("My card was stolen and I think funds are compromised")
    assert result.team == "payments"
    assert result.severity == "critical"

def test_vip_escalates_medium_result_to_high():
    result = route_message("My withdrawal is delayed", customer_tier="vip")
    assert result.team == "payments"
    assert result.severity == "high"

def test_critical_keyword_overrides_unmatched_result():
    result = route_message("I think I was hacked")
    assert result.team == "general"
    assert result.severity == "critical"

def test_vip_does_not_downgrade_critical_result():
    result = route_message("My account was compromised", customer_tier="vip")
    assert result.team == "accounts"
    assert result.severity == "critical"

def test_stolen_is_not_a_global_override():
    result = route_message("My bicycle was stolen")
    assert result.team == "general"
    assert result.severity == "low"

def test_unknown_message_goes_to_general():
    result = route_message("I have a question about something unrelated")
    assert result.team == "general"
    assert result.severity == "low"

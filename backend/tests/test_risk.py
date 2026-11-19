from risk_assessment.engine import assess, severity_from_score


def test_transparent_high_confidence_high_severity():
    finding = {
        "base_severity": "high",
        "confidence": "high",
        "verified": True,
        "exploitability": "moderate",
        "affected_endpoints": 1,
        "weakness_count": 0,
    }
    result = assess(finding)
    assert result["severity"] == "high"
    assert result["risk_score"] == 76.0
    assert result["model_source"] == "rule-based-transparent"
    assert any("Final score" in line for line in result["reasoning"])


def test_low_confidence_reduces_score():
    finding = {
        "base_severity": "medium",
        "confidence": "low",
        "verified": False,
        "exploitability": "low",
        "affected_endpoints": 1,
    }
    result = assess(finding)
    assert result["risk_score"] < 52
    assert result["severity"] in {"low", "medium"}


def test_severity_thresholds():
    assert severity_from_score(90) == "critical"
    assert severity_from_score(75) == "high"
    assert severity_from_score(50) == "medium"
    assert severity_from_score(25) == "low"
    assert severity_from_score(5) == "informational"


def test_scope_factor_is_bounded():
    finding = {
        "base_severity": "medium",
        "confidence": "high",
        "exploitability": "low",
        "affected_endpoints": 500,
    }
    result = assess(finding)
    assert result["risk_score"] <= 100
    assert result["components"]["endpoint_factor"] == 1.24

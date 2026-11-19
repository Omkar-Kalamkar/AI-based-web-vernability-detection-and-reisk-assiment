from scanners.checks import check_security_headers, check_xss_indicators, reduce_findings
from scanners.http_client import FetchResult
from scanners.url_guard import TargetValidationError, check_ip, normalize_target


def _response(url, headers=None, body=""):
    return FetchResult(url=url, status_code=200, headers=headers or {}, body=body, set_cookie_headers=[])


def test_normalize_target():
    url, host, port, scheme = normalize_target("HTTP://127.0.0.1:8000/path?q=1")
    assert url == "http://127.0.0.1:8000/path?q=1"
    assert host == "127.0.0.1"
    assert port == 8000
    assert scheme == "http"


def test_metadata_host_blocked():
    try:
        check_ip("169.254.169.254", "169.254.169.254", 80)
    except TargetValidationError:
        return
    raise AssertionError("Cloud metadata endpoint should be blocked")


def test_lab_loopback_allowed_for_allowed_host():
    assert str(check_ip("127.0.0.1", "127.0.0.1", 8000)) == "127.0.0.1"


def test_missing_headers_detected():
    findings = check_security_headers([_response("http://127.0.0.1:8000/")], is_https=False)
    names = {item["name"] for item in findings}
    assert "Missing Content-Security-Policy" in names
    assert "Missing X-Frame-Options" in names
    assert all(item["verified"] for item in findings)


def test_reduce_findings_merges_duplicates():
    first = {
        "key": "missing_csp",
        "name": "Missing CSP",
        "category": "Security Headers",
        "evidence": "a",
        "confidence": "high",
        "verified": True,
        "affected_endpoints": 1,
        "weakness_count": 1,
    }
    second = {**first, "evidence": "longer evidence text", "affected_endpoints": 3}
    merged = reduce_findings([first, second])
    assert len(merged) == 1
    assert merged[0]["affected_endpoints"] == 3
    assert merged[0]["evidence"] == "longer evidence text"


def test_benign_probe_not_reported_as_exploit():
    class FakeFetcher:
        def fetch(self, url):
            return _response(url, {}, '<html><script>var x = "secureai-abc123";</script></html>')

    findings = check_xss_indicators(FakeFetcher(), "http://127.0.0.1:8000/", "secureai-abc123")
    assert findings
    assert findings[0]["verified"] is False
    assert findings[0]["meta"]["no_payload_sent"] is True

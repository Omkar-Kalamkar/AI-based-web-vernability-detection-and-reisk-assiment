"""Passive checks and false-positive reduction for observed HTTP evidence."""

import re
from collections import OrderedDict
from datetime import datetime, timezone

from scanners.url_guard import TargetValidationError

OWASP = {
    "headers": "https://owasp.org/www-project-secure-headers/",
    "csp": "https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/05-Authorization_Testing/",
    "tls": "https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/09-Testing_for_Weak_Cryptography/",
    "cookies": "https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/06-Session_Management_Testing/02-Testing_for_Cookies_Attributes",
    "info": "https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/01-Information_Gathering/",
    "config": "https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/02-Configuration_and_Deployment_Management_Testing/",
    "xss": "https://owasp.org/www-community/attacks/xss/",
    "sqli": "https://owasp.org/www-community/attacks/SQL_Injection",
}


def make_finding(
    key,
    name,
    category,
    base_severity,
    evidence,
    description,
    impact,
    recommendation,
    references=None,
    confidence="high",
    verified=True,
    exploitability="low",
    endpoints=1,
    weakness_count=0,
    meta=None,
):
    return {
        "key": key,
        "name": name,
        "category": category,
        "base_severity": base_severity,
        "confidence": confidence,
        "verified": bool(verified),
        "evidence": str(evidence)[:1500],
        "description": description,
        "impact": impact,
        "recommendation": recommendation,
        "references": references or [],
        "exploitability": exploitability,
        "affected_endpoints": max(1, int(endpoints)),
        "weakness_count": weakness_count,
        "meta": meta or {},
    }


def _snippet(text, pattern, radius=110):
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if not match:
        return text[:250]
    start = max(0, match.start() - radius)
    end = min(len(text), match.end() + radius)
    return re.sub(r"\s+", " ", text[start:end]).strip()[:400]


def check_security_headers(responses, is_https):
    specs = [
        (
            "content-security-policy",
            "missing_csp",
            "Missing Content-Security-Policy",
            "high" if is_https else "medium",
            "Content-Security-Policy tells the browser which scripts, styles and other resources may load. It is absent from the response.",
            "Without a policy, injected scripts from other origins can execute more easily in a victim's browser.",
            "Add a restrictive Content-Security-Policy header, for example: default-src 'self'; script-src 'self'; object-src 'none'; base-uri 'self'.",
            [OWASP["headers"], "https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP"],
            "moderate",
        ),
        (
            "x-frame-options",
            "missing_xframe",
            "Missing X-Frame-Options",
            "medium",
            "The response does not include X-Frame-Options, and no equivalent frame-ancestors directive was observed in the CSP.",
            "The page may be embedded in an attacker-controlled iframe, which can enable clickjacking attacks.",
            "Send 'X-Frame-Options: DENY' or 'SAMEORIGIN', and add 'frame-ancestors' to the Content-Security-Policy header.",
            [OWASP["headers"]],
            "moderate",
        ),
        (
            "strict-transport-security",
            "missing_hsts",
            "Missing HTTP Strict-Transport-Security",
            "high" if is_https else "medium",
            "The HTTPS response does not advertise Strict-Transport-Security with a long max-age.",
            "Browsers can be tricked into using plain HTTP, exposing cookies and session data to network attackers.",
            "Send 'Strict-Transport-Security: max-age=31536000; includeSubDomains' on all HTTPS responses.",
            [OWASP["tls"]],
            "moderate",
        ),
        (
            "x-content-type-options",
            "missing_nosniff",
            "Missing X-Content-Type-Options",
            "medium",
            "The response does not include 'X-Content-Type-Options: nosniff'.",
            "Browsers may sniff a file as executable script or HTML even when the server declared a different content type.",
            "Send 'X-Content-Type-Options: nosniff' on every response, especially for user-uploaded content.",
            [OWASP["headers"]],
            "low",
        ),
        (
            "referrer-policy",
            "missing_referrer_policy",
            "Missing Referrer-Policy",
            "low",
            "The response does not define how much referrer information browsers may disclose.",
            "Full URLs in the Referer header may leak internal paths, tokens or search terms to third parties.",
            "Send 'Referrer-Policy: strict-origin-when-cross-origin' or a stricter value.",
            [OWASP["headers"]],
            "low",
        ),
        (
            "permissions-policy",
            "missing_permissions_policy",
            "Missing Permissions-Policy",
            "low",
            "The response does not restrict powerful browser features such as camera, microphone or geolocation.",
            "Compromised scripts may be able to request access to sensitive browser capabilities.",
            "Send a restrictive Permissions-Policy header, for example: camera=(), microphone=(), geolocation=().",
            [OWASP["headers"]],
            "low",
        ),
    ]
    findings = []
    for header, key, name, severity, description, impact, recommendation, refs, exploitability in specs:
        missing = [r for r in responses if not r.headers.get(header)]
        if not missing:
            continue
        evidence = f"Header '{header}' was not present in {len(missing)} of {len(responses)} inspected response(s)."
        evidence += " Examples: " + ", ".join(r.url for r in missing[:3])
        findings.append(
            make_finding(
                key,
                name,
                "Security Headers",
                severity,
                evidence,
                description,
                impact,
                recommendation,
                refs,
                exploitability=exploitability,
                endpoints=len(missing),
                weakness_count=1,
            )
        )
    return findings


def check_csp_configuration(responses):
    csp_response = next((r for r in responses if r.headers.get("content-security-policy")), None)
    if csp_response is None:
        return []
    csp = csp_response.headers["content-security-policy"]
    lower = csp.lower()
    findings = []
    rules = [
        ("unsafe_inline", "unsafe-inline" in lower, "medium", "CSP allows inline scripts or styles via 'unsafe-inline'.", "Inline script execution weakens protection against reflected XSS.", "Use nonces or hashes instead of 'unsafe-inline'."),
        ("unsafe_eval", "unsafe-eval" in lower, "medium", "CSP allows dynamic code execution via 'unsafe-eval'.", "eval-like functions make DOM-based XSS exploitation easier.", "Remove 'unsafe-eval' and refactor code that depends on eval."),
        ("wildcard_source", bool(re.search(r"(?:default-src|script-src)\s+[^;]*\*", lower)), "medium", "CSP uses a wildcard source for scripts or default sources.", "A wildcard source permits loading executable resources from unintended origins.", "Replace wildcards with explicit trusted origins."),
        ("no_object_src", "object-src" not in lower, "low", "CSP does not declare an object-src directive.", "Legacy plugins can still be loaded if default-src is permissive.", "Add 'object-src 'none'' to the policy."),
        ("no_base_uri", "base-uri" not in lower, "low", "CSP does not declare a base-uri directive.", "An attacker may be able to hijack relative resource URLs via a injected base tag.", "Add 'base-uri 'self'' to the policy."),
        ("no_frame_ancestors", "frame-ancestors" not in lower, "medium", "CSP does not declare frame-ancestors.", "Framing protection relies only on X-Frame-Options, which is inconsistently supported.", "Add 'frame-ancestors 'none'' or a trusted origin list."),
    ]
    for key, present, severity, description, impact, recommendation in rules:
        if not present:
            continue
        findings.append(
            make_finding(
                key,
                f"Weak Content-Security-Policy configuration ({key.replace('_', ' ')})",
                "Content Security Policy",
                severity,
                f"Observed CSP: {csp[:700]}",
                description,
                impact,
                recommendation,
                [OWASP["headers"], "https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP"],
                exploitability="low",
                endpoints=1,
                weakness_count=1,
            )
        )
    return findings


def check_frame_configuration(responses):
    findings = []
    for response in responses:
        value = response.headers.get("x-frame-options")
        if not value or value.strip().lower() in {"deny", "sameorigin"}:
            continue
        findings.append(
            make_finding(
                "weak_xframe",
                "Deprecated X-Frame-Options value",
                "Security Headers",
                "low",
                f"X-Frame-Options: {value}",
                "The configured framing value is deprecated or not standardised across browsers.",
                "Some browsers may ignore it, leaving the page vulnerable to framing attacks.",
                "Use 'X-Frame-Options: SAMEORIGIN' together with CSP frame-ancestors.",
                [OWASP["headers"]],
            )
        )
        break
    return findings


def check_hsts_configuration(responses):
    response = next((r for r in responses if r.headers.get("strict-transport-security")), None)
    if response is None:
        return []
    hsts = response.headers["strict-transport-security"]
    findings = []
    match = re.search(r"max-age\s*=\s*(\d+)", hsts, re.IGNORECASE)
    if match and int(match.group(1)) < 31536000:
        findings.append(
            make_finding(
                "weak_hsts_max_age",
                "Short HTTP Strict-Transport-Security max-age",
                "Transport Security",
                "medium",
                f"Strict-Transport-Security: {hsts}",
                "The HSTS max-age is shorter than the recommended 31536000 seconds (one year).",
                "A short lifetime leaves a window where downgrade attacks are possible after the header expires.",
                "Set max-age to at least 31536000 seconds.",
                [OWASP["tls"]],
            )
        )
    if "includesubdomains" not in hsts.lower():
        findings.append(
            make_finding(
                "hsts_no_subdomains",
                "HSTS does not include subdomains",
                "Transport Security",
                "low",
                f"Strict-Transport-Security: {hsts}",
                "The HSTS policy applies only to the exact host, not to its subdomains.",
                "Subdomains that handle sessions could still be downgraded to HTTP.",
                "Add 'includeSubDomains' after confirming all subdomains support HTTPS.",
                [OWASP["tls"]],
            )
        )
    return findings


def check_https_and_tls(target, responses):
    findings = []
    if target["scheme"] == "http":
        findings.append(
            make_finding(
                "http_not_enforced",
                "Unencrypted HTTP transport",
                "Transport Security",
                "high",
                f"Target was served over http://{target['host']}:{target['port']}{target['url'].split(target['host'])[-1]} without TLS.",
                "The application is reachable over plain HTTP, so traffic can be read or modified in transit.",
                "Credentials, cookies and application data may be intercepted on shared or hostile networks.",
                "Serve the application over HTTPS, redirect HTTP traffic to HTTPS, and enable HSTS.",
                [OWASP["tls"]],
                exploitability="moderate",
                endpoints=1,
                weakness_count=1,
            )
        )
        return findings

    import socket
    import ssl

    from config import Config

    host, port = target["host"], target["port"]
    try:
        context = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=Config.SCAN_CONNECT_TIMEOUT) as raw_socket:
            with context.wrap_socket(raw_socket, server_hostname=host) as tls_socket:
                version = tls_socket.version() or ""
                cert = tls_socket.getpeercert()
    except ssl.SSLCertVerificationError as exc:
        findings.append(
            make_finding(
                "invalid_tls_certificate",
                "Invalid or untrusted TLS certificate",
                "Transport Security",
                "high",
                f"TLS verification failed: {str(exc)[:300]}",
                "The server certificate could not be validated against trusted certificate authorities or the requested hostname.",
                "Users may be exposed to man-in-the-middle attacks or misleading browser warnings.",
                "Install a valid certificate that matches the hostname and renew it before expiry.",
                [OWASP["tls"]],
                exploitability="moderate",
            )
        )
        return findings
    except ssl.SSLError as exc:
        findings.append(
            make_finding(
                "tls_handshake_failed",
                "TLS handshake failure",
                "Transport Security",
                "medium",
                f"TLS negotiation failed: {str(exc)[:300]}",
                "A trusted TLS connection could not be negotiated with the target.",
                "Clients may fall back to weaker protocols or be unable to connect securely.",
                "Configure modern TLS versions and a complete certificate chain.",
                [OWASP["tls"]],
            )
        )
        return findings
    except OSError:
        return []

    if version and version < "TLSv1.2":
        findings.append(
            make_finding(
                "weak_tls_version",
                "Outdated TLS protocol version",
                "Transport Security",
                "high",
                f"Negotiated protocol: {version}",
                "The server negotiated a TLS version older than 1.2.",
                "Older protocol versions are affected by known weaknesses and are prohibited by modern compliance standards.",
                "Disable TLS 1.0 and 1.1 and enable TLS 1.2 or TLS 1.3 only.",
                [OWASP["tls"]],
                exploitability="moderate",
            )
        )

    if cert and cert.get("notAfter"):
        try:
            expires = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
            days_left = (expires - datetime.now(timezone.utc)).days
            if days_left < 14:
                findings.append(
                    make_finding(
                        "tls_cert_expiring",
                        "TLS certificate expiring soon",
                        "Transport Security",
                        "medium" if days_left >= 0 else "high",
                        f"Certificate expires: {cert['notAfter']} ({days_left} days remaining)",
                        "The server certificate expires within 14 days or has already expired.",
                        "An expired certificate causes browser warnings and can interrupt trusted access.",
                        "Renew the certificate and automate renewal before expiry.",
                        [OWASP["tls"]],
                    )
                )
        except (ValueError, TypeError):
            pass
    return findings


def check_cookies(responses):
    from http.cookies import SimpleCookie

    observed = OrderedDict()
    for response in responses:
        for raw in response.set_cookie_headers:
            jar = SimpleCookie()
            try:
                jar.load(raw)
            except Exception:
                continue
            for name, morsel in jar.items():
                observed.setdefault(name, []).append((morsel, raw, response.url))

    findings = []
    for name, entries in observed.items():
        session_like = bool(re.search(r"session|sess|auth|token|sid|jsessionid|phpsessid", name, re.IGNORECASE))
        evidence_lines = [raw[:250] for _morsel, raw, _url in entries[:3]]

        def missing(attr):
            return sum(1 for morsel, _raw, _url in entries if attr not in morsel)

        if missing("httponly"):
            findings.append(
                make_finding(
                    "cookie_missing_httponly",
                    f"Cookie '{name}' lacks HttpOnly flag",
                    "Cookie Security",
                    "high" if session_like else "medium",
                    "Observed Set-Cookie: " + " | ".join(evidence_lines),
                    f"The cookie '{name}' is set without the HttpOnly attribute, so client-side scripts can read it.",
                    "If an XSS flaw exists, session cookies could be stolen and reused by an attacker.",
                    f"Add 'HttpOnly' when setting the '{name}' cookie unless JavaScript genuinely needs access.",
                    [OWASP["cookies"]],
                    exploitability="moderate" if session_like else "low",
                    endpoints=len(entries),
                    weakness_count=1,
                )
            )
        if missing("secure"):
            findings.append(
                make_finding(
                    "cookie_missing_secure",
                    f"Cookie '{name}' lacks Secure flag",
                    "Cookie Security",
                    "high" if session_like else "medium",
                    "Observed Set-Cookie: " + " | ".join(evidence_lines),
                    f"The cookie '{name}' can be transmitted over an unencrypted HTTP connection.",
                    "A network attacker could capture the cookie and impersonate the user.",
                    f"Add the 'Secure' attribute to '{name}' and serve the application over HTTPS.",
                    [OWASP["cookies"]],
                    exploitability="moderate" if session_like else "low",
                    endpoints=len(entries),
                    weakness_count=1,
                )
            )
        no_samesite = sum(
            1 for morsel, _raw, _url in entries if "samesite" not in morsel or not morsel.get("samesite")
        )
        if no_samesite:
            findings.append(
                make_finding(
                    "cookie_missing_samesite",
                    f"Cookie '{name}' lacks SameSite attribute",
                    "Cookie Security",
                    "medium" if session_like else "low",
                    "Observed Set-Cookie: " + " | ".join(evidence_lines),
                    f"The cookie '{name}' does not declare a SameSite policy.",
                    "Cross-site requests may include the cookie, increasing exposure to CSRF attacks.",
                    "Set 'SameSite=Lax' or 'SameSite=Strict' for session cookies.",
                    [OWASP["cookies"]],
                    exploitability="low",
                    endpoints=len(entries),
                    weakness_count=1,
                )
            )
    return findings


INFO_HEADERS = [
    ("server", "server_header", "Server header discloses software information", "informational"),
    ("x-powered-by", "powered_by_header", "X-Powered-By header discloses technology stack", "low"),
    ("x-aspnet-version", "aspnet_version_header", "ASP.NET version disclosed in response header", "low"),
    ("x-aspnetmvc-version", "aspnet_mvc_version_header", "ASP.NET MVC version disclosed in response header", "low"),
    ("x-debug-token", "debug_token_header", "Debug token exposed in response header", "medium"),
    ("x-debug-duration", "debug_duration_header", "Debug timing exposed in response header", "low"),
]


def check_information_disclosure(responses):
    findings = []
    for header, key, name, severity in INFO_HEADERS:
        matches = [r for r in responses if r.headers.get(header)]
        if not matches:
            continue
        values = sorted({r.headers[header][:180] for r in matches})
        findings.append(
            make_finding(
                key,
                name,
                "Information Disclosure",
                severity,
                f"Header '{header}' exposed value(s): {', '.join(values[:3])}",
                f"The application reveals '{header}', which identifies implementation details.",
                "Attackers can use technology and version details to look for known vulnerabilities in that stack.",
                f"Remove or genericise the '{header}' header in web server and application configuration.",
                [OWASP["info"]],
                exploitability="low",
                endpoints=len(matches),
            )
        )
    return findings


LISTING_MARKERS = [
    (r"<title>\s*index of\b", "HTML title says 'Index of'"),
    (r"<h1[^>]*>\s*index of\b", "HTML heading says 'Index of'"),
    (r"\bparent directory\b", "Page contains a 'Parent Directory' link"),
    (r"\bdirectory listing\b", "Page identifies itself as a directory listing"),
]


def check_directory_listing(responses):
    findings = []
    for response in responses:
        for pattern, description in LISTING_MARKERS:
            match = re.search(pattern, response.body, re.IGNORECASE)
            if match:
                findings.append(
                    make_finding(
                        "directory_listing",
                        "Directory listing indicator",
                        "Configuration",
                        "medium",
                        f"{description}. Snippet: {_snippet(response.body, pattern)}",
                        "A web directory appears to present a browsable list of its files.",
                        "File listings can expose backups, configuration files or other unintended resources.",
                        "Disable directory indexes in the web server and add an index file or access rules for public directories.",
                        [OWASP["config"]],
                        exploitability="low",
                        endpoints=1,
                    )
                )
                break
    return findings


def _with_query_param(url, key, value):
    from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query[key] = value
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), ""))


def check_xss_indicators(fetcher, base_url, probe):
    probe_url = _with_query_param(base_url, "secureai_probe", probe)
    response = fetcher.fetch(probe_url)
    if not response.ok or probe not in response.body or not probe:
        return []

    scripts = " ".join(re.findall(r"<script[^>]*>(.*?)</script>", response.body, re.IGNORECASE | re.DOTALL))
    in_script = probe in scripts
    in_attribute = bool(re.search(r"<[^>]+=\s*[\"']?" + re.escape(probe), response.body, re.IGNORECASE))
    dangerous_api = bool(re.search(r"innerHTML|document\.write|\beval\s*\(", scripts, re.IGNORECASE))

    if in_script or in_attribute:
        context = "JavaScript string/expression" if in_script else "HTML attribute"
        confidence = "medium" if dangerous_api or in_script else "low"
        return [
            make_finding(
                "potential_reflected_xss",
                "Potential reflected XSS indicator (benign probe)",
                "Cross-Site Scripting (Potential)",
                "medium",
                f"A harmless random marker was reflected inside a {context} at {response.url}. Evidence: {_snippet(response.body, re.escape(probe))}",
                "A harmless random value supplied in a query parameter was copied into executable browser context. This is an indicator, not a confirmed exploit.",
                "If the application does not encode this input contextually, an attacker could inject script that runs in other users' browsers.",
                "Encode output for its destination context, use safe DOM APIs instead of innerHTML, and deploy a strict Content-Security-Policy.",
                [OWASP["xss"], OWASP["headers"]],
                confidence=confidence,
                verified=False,
                exploitability="moderate" if dangerous_api else "low",
                endpoints=1,
                weakness_count=1 if dangerous_api else 0,
                meta={"probe": "benign-random-marker", "no_payload_sent": True, "probe_url": response.url},
            )
        ]

    return [
        make_finding(
            "input_reflected",
            "User input reflected in response (informational)",
            "Input Handling",
            "informational",
            f"Harmless marker was present as plain text at {response.url}. Evidence: {_snippet(response.body, re.escape(probe))}",
            "A query parameter value is reflected in the page body as regular text. No executable context was observed.",
            "Reflection alone is not an exploit; it is recorded so output encoding can be reviewed.",
            "Continue to apply context-aware output encoding when rendering user-controlled values.",
            [OWASP["xss"]],
            confidence="medium",
            verified=False,
            exploitability="low",
            meta={"probe": "benign-random-marker", "no_payload_sent": True, "probe_url": response.url},
        )
    ]


SQLI_SIGNATURES = [
    (r"SQL syntax", "SQL syntax error text"),
    (r"mysql_fetch_|mysql_", "MySQL error text"),
    (r"ORA-\d{4,5}", "Oracle database error code"),
    (r"PG::SyntaxError|psycopg2\.", "PostgreSQL error text"),
    (r"sqlite3\.OperationalError|unrecognized token", "SQLite error text"),
    (r"unclosed quotation mark", "Unclosed quotation mark error"),
    (r"Microsoft OLE DB Provider for SQL Server", "SQL Server provider error"),
    (r"SQLSTATE\[", "SQLSTATE error code"),
]


def check_sqli_indicators(responses):
    findings = []
    for response in responses:
        for pattern, label in SQLI_SIGNATURES:
            if re.search(pattern, response.body, re.IGNORECASE):
                findings.append(
                    make_finding(
                        "potential_sqli_error",
                        "Potential SQL error disclosure indicator",
                        "SQL Injection (Potential)",
                        "medium",
                        f"{label} was present in the HTTP response body at {response.url}. Evidence: {_snippet(response.body, pattern)}",
                        "Database error details were observed in a normal application response. This may indicate that input reaches a SQL query.",
                        "Error messages can reveal query structure and help an attacker refine an injection attack, even though this scan did not test exploitation.",
                        "Use parameterised queries, suppress detailed database errors in production, and log errors server-side instead of displaying them.",
                        [OWASP["sqli"]],
                        confidence="low",
                        verified=False,
                        exploitability="low",
                        endpoints=1,
                        meta={"no_payload_sent": True},
                    )
                )
                break
    return findings


def reduce_findings(findings):
    """Merge duplicates and discard observations without supporting evidence."""
    merged = OrderedDict()
    for finding in findings:
        if not finding.get("evidence") or not finding.get("name"):
            continue
        key = (finding["key"], finding["name"], finding["category"])
        existing = merged.get(key)
        if existing is None:
            merged[key] = finding
            continue
        existing["affected_endpoints"] = max(existing["affected_endpoints"], finding["affected_endpoints"])
        existing["weakness_count"] = max(existing["weakness_count"], finding.get("weakness_count", 0))
        if finding["verified"]:
            existing["verified"] = True
        ranks = {"high": 3, "medium": 2, "low": 1}
        if ranks.get(finding["confidence"], 0) > ranks.get(existing["confidence"], 0):
            existing["confidence"] = finding["confidence"]
        if len(finding["evidence"]) > len(existing["evidence"]):
            existing["evidence"] = finding["evidence"]
    return list(merged.values())

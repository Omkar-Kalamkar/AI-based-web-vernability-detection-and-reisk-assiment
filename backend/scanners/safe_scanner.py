"""Orchestrates a safe, read-only scan and persists results."""

import json
import secrets
import threading
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup

from ai_engine.explainer import explain
from config import Config
from database import SessionLocal
from models.scan import Scan
from models.user import utcnow
from models.vulnerability import Vulnerability
from risk_assessment.engine import assess
from routes.deps import db_session
from scanners.checks import (
    check_cookies,
    check_csp_configuration,
    check_directory_listing,
    check_frame_configuration,
    check_hsts_configuration,
    check_https_and_tls,
    check_information_disclosure,
    check_security_headers,
    check_sqli_indicators,
    check_xss_indicators,
    reduce_findings,
)
from scanners.http_client import SafeFetcher
from scanners.url_guard import TargetValidationError, validate_target
from scanners.zap import collect_zap_findings

SEVERITY_PENALTY = {"critical": 30, "high": 12, "medium": 6, "low": 3, "informational": 1}
SKIP_LINK_WORDS = ("logout", "signout", "delete", "remove", "reset", "destroy", "checkout", "payment", "confirm", "submit")


def _update(scan_id, **kwargs):
    with db_session() as db:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if scan is None:
            return
        for key, value in kwargs.items():
            setattr(scan, key, value)
        db.commit()


def _same_origin(url, target):
    parts = urlsplit(url)
    port = parts.port or (443 if parts.scheme.lower() == "https" else 80)
    return parts.hostname == target["host"] and port == target["port"]


def _discover_links(landing, target, limit):
    soup = BeautifulSoup(landing.body, "html.parser")
    found = []
    seen = {landing.url}
    for anchor in soup.find_all("a", href=True):
        href = anchor["href"].strip()
        if not href or href.startswith(("#", "javascript:", "mailto:", "tel:", "data:")):
            continue
        if any(word in href.lower() for word in SKIP_LINK_WORDS):
            continue
        absolute = urljoin(landing.url, href)
        if not absolute.lower().startswith(("http://", "https://")) or not _same_origin(absolute, target):
            continue
        absolute = absolute.split("#")[0]
        if absolute in seen:
            continue
        seen.add(absolute)
        found.append(absolute)
        if len(found) >= max(0, limit - 1):
            break
    for path in ("/uploads/", "/files/"):
        candidate = urljoin(landing.url, path)
        if candidate not in seen and len(found) < max(0, limit - 1):
            seen.add(candidate)
            found.append(candidate)
    return found


def _score_scan(findings):
    penalty = sum(SEVERITY_PENALTY.get(item["severity"], 1) for item in findings)
    return max(0, 100 - penalty)


def run_scan(scan_id):
    from database import SessionLocal as LocalSession

    with LocalSession() as db:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if scan is None:
            return
        target_url = scan.target_url
        scan.status = "running"
        scan.progress = 5
        scan.stage = "Validating target scope and authorization"
        scan.started_at = utcnow()
        db.commit()

    fetcher = None
    try:
        target = validate_target(target_url)
        _update(scan_id, progress=12, stage="Fetching authorized landing page")
        fetcher = SafeFetcher(target)
        landing = fetcher.fetch(target["url"])
        if not landing.ok:
            _update(
                scan_id,
                status="failed",
                progress=100,
                stage="Failed",
                error=f"Target did not respond: {landing.error}",
                completed_at=utcnow(),
            )
            return

        max_pages = max(1, min(Config.MAX_PAGES_PER_SCAN, 20))
        _update(scan_id, progress=22, stage="Inspecting same-origin links (limited crawl)")
        responses = [landing]
        for link in _discover_links(landing, target, max_pages):
            result = fetcher.fetch(link)
            if result.ok:
                responses.append(result)
            if len(responses) >= max_pages:
                break
        _update(scan_id, progress=38, stage="Sending one benign reflection probe", pages_scanned=len(responses))

        probe = "secureai-" + secrets.token_hex(6)
        findings = []
        findings.extend(check_security_headers(responses, target["scheme"] == "https"))
        findings.extend(check_csp_configuration(responses))
        findings.extend(check_frame_configuration(responses))
        findings.extend(check_hsts_configuration(responses))
        findings.extend(check_https_and_tls(target, responses))
        findings.extend(check_xss_indicators(fetcher, target["url"], probe))

        _update(scan_id, progress=58, stage="Analyzing cookies, disclosure and directory indicators")
        findings.extend(check_cookies(responses))
        findings.extend(check_information_disclosure(responses))
        findings.extend(check_directory_listing(responses))
        findings.extend(check_sqli_indicators(responses))
        findings.extend(collect_zap_findings(target["host"]))

        _update(scan_id, progress=74, stage="Validating evidence and reducing false positives")
        findings = reduce_findings(findings)

        _update(scan_id, progress=86, stage="Running transparent risk scoring and local AI explanations")
        enriched = []
        for finding in findings:
            assessment = assess(finding)
            enriched.append({**finding, **assessment, **explain(finding)})

        counts = {key: 0 for key in SEVERITY_PENALTY}
        for item in enriched:
            counts[item["severity"]] = counts.get(item["severity"], 0) + 1

        security_score = _score_scan(enriched)
        with LocalSession() as db:
            scan = db.query(Scan).filter(Scan.id == scan_id).first()
            if scan is None:
                return
            for item in enriched:
                db.add(
                    Vulnerability(
                        id="vuln_" + secrets.token_hex(10),
                        scan_id=scan_id,
                        name=item["name"][:255],
                        category=item["category"][:120],
                        severity=item["severity"],
                        risk_score=item["risk_score"],
                        confidence=item["confidence"],
                        verified=1 if item.get("verified") else 0,
                        affected_url=item.get("meta", {}).get("probe_url", landing.url)[:2048],
                        description=item["description"],
                        impact=item["impact"],
                        evidence=item["evidence"],
                        recommendation=item["recommendation"],
                        simple_explanation=item["simple_explanation"],
                        why_dangerous=item["why_dangerous"],
                        secure_coding=item["secure_coding"],
                        prevention=item["prevention"],
                        references=json.dumps(item.get("references", [])),
                        affected_endpoints=item["affected_endpoints"],
                        exploitability=item["exploitability"],
                        model_source=item["model_source"],
                        reasoning=json.dumps(item["reasoning"]),
                    )
                )
            scan.status = "completed"
            scan.progress = 100
            scan.stage = "Completed"
            scan.pages_scanned = len(responses)
            scan.security_score = security_score
            scan.total_findings = len(enriched)
            scan.critical_count = counts["critical"]
            scan.high_count = counts["high"]
            scan.medium_count = counts["medium"]
            scan.low_count = counts["low"]
            scan.info_count = counts["informational"]
            scan.completed_at = utcnow()
            db.commit()
    except TargetValidationError as exc:
        _update(scan_id, status="failed", progress=100, stage="Failed", error=str(exc), completed_at=utcnow())
    except Exception as exc:
        _update(
            scan_id,
            status="failed",
            progress=100,
            stage="Failed",
            error=f"Scan could not be completed: {type(exc).__name__}",
            completed_at=utcnow(),
        )
    finally:
        if fetcher is not None:
            fetcher.close()


def start_scan_worker(scan_id):
    thread = threading.Thread(target=run_scan, args=(scan_id,), daemon=True, name=f"secureai-scan-{scan_id[:8]}")
    thread.start()
    return thread

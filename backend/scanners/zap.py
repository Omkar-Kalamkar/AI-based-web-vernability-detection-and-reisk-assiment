"""Optional OWASP ZAP integration.

Only reads alerts already collected by a ZAP instance the user controls.
It never starts an active attack and is disabled unless OWASP_ZAP_URL is configured.
"""

from urllib.parse import urlsplit

import requests

from config import Config

ZAP_TIMEOUT = 4


def zap_status():
    if not Config.OWASP_ZAP_URL:
        return {"configured": False, "connected": False, "message": "OWASP_ZAP_URL is not configured"}
    try:
        response = requests.get(
            f"{Config.OWASP_ZAP_URL.rstrip('/')}/JSON/core/view/version/",
            params={"apikey": Config.OWASP_ZAP_API_KEY} if Config.OWASP_ZAP_API_KEY else None,
            timeout=ZAP_TIMEOUT,
        )
        if response.ok:
            return {"configured": True, "connected": True, "version": response.text.strip()[:100]}
        return {"configured": True, "connected": False, "message": f"ZAP returned HTTP {response.status_code}"}
    except requests.RequestException:
        return {"configured": True, "connected": False, "message": "ZAP instance is unreachable"}


def collect_zap_findings(target_host):
    """Read-only: fetch alerts ZAP has already recorded for this host."""
    if not Config.OWASP_ZAP_URL or not zap_status()["connected"]:
        return []
    try:
        response = requests.get(
            f"{Config.OWASP_ZAP_URL.rstrip('/')}/JSON/alert/view/alerts/",
            params={
                "baseurl": f"http://{target_host}",
                "apikey": Config.OWASP_ZAP_API_KEY,
            },
            timeout=ZAP_TIMEOUT,
        )
        alerts = response.json().get("alerts", []) if response.ok else []
    except (requests.RequestException, ValueError):
        return []

    findings = []
    for alert in alerts[:20]:
        name = str(alert.get("alert", "ZAP alert"))
        risk = str(alert.get("risk", "Informational")).lower()
        severity = {"high": "high", "medium": "medium", "low": "low", "informational": "informational"}.get(risk, "informational")
        if "zap" not in name.lower():
            name = f"ZAP passive alert: {name}"
        findings.append(
            {
                "key": "zap_" + str(alert.get("pluginid", "alert")),
                "name": name[:255],
                "category": "OWASP ZAP Alert",
                "base_severity": severity,
                "confidence": "medium",
                "verified": False,
                "evidence": str(alert.get("evidence", ""))[:800] or str(alert.get("description", ""))[:800],
                "description": str(alert.get("description", "Alert reported by the configured OWASP ZAP instance."))[:1500],
                "impact": str(alert.get("description", "Review the alert in ZAP for impact details."))[:800],
                "recommendation": str(alert.get("solution", "Follow the OWASP guidance for this alert type."))[:800],
                "references": [str(alert.get("reference", "https://owasp.org/"))],
                "exploitability": "low",
                "affected_endpoints": 1,
                "weakness_count": 0,
                "meta": {"source": "owasp-zap-read-only"},
            }
        )
    return findings

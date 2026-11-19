"""Local AI-style explanation generator (no external API or secret required)."""

from ai_engine.knowledge import explanation_for


def explain(finding):
    simple, dangerous, secure_coding, prevention = explanation_for(finding.get("key", ""), finding.get("category", ""))
    recommendation = finding.get("recommendation", "")
    combined_recommendation = recommendation if recommendation else secure_coding
    return {
        "simple_explanation": simple,
        "why_dangerous": dangerous,
        "recommendation": combined_recommendation,
        "secure_coding": secure_coding,
        "prevention": prevention,
        "explanation_source": "local-knowledge-based-generator",
    }


def summarize(scan, findings):
    by_severity = {}
    for finding in findings:
        by_severity[finding["severity"]] = by_severity.get(finding["severity"], 0) + 1
    top = sorted(findings, key=lambda item: -item["risk_score"])[:5]
    verified = sum(1 for item in findings if item.get("verified"))
    return {
        "security_score": scan.security_score,
        "risk_summary": (
            "The application shows several high-impact configuration weaknesses."
            if scan.security_score < 50
            else "The application has a moderate security posture with findings that should be remediated."
            if scan.security_score < 80
            else "The application shows a strong baseline with a small number of issues to review."
        ),
        "severity_distribution": by_severity,
        "confirmed_findings": verified,
        "potential_indicators": len(findings) - verified,
        "top_risks": [
            {
                "name": item["name"],
                "severity": item["severity"],
                "risk_score": item["risk_score"],
                "reasoning": item.get("reasoning", [])[:3],
            }
            for item in top
        ],
        "recommended_next_steps": [
            "Remediate critical and high findings first.",
            "Re-scan after each change to compare the security score.",
            "Manually review potential indicators before treating them as confirmed vulnerabilities.",
        ],
    }

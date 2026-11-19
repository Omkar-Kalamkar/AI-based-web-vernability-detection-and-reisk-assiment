"""Transparent weighted risk scoring with optional synthetic-data ML assistance."""

from config import Config
from risk_assessment.ml_model import get_model

BASE_WEIGHTS = {"critical": 92.0, "high": 76.0, "medium": 52.0, "low": 26.0, "informational": 10.0}
CONFIDENCE_WEIGHTS = {"high": 1.0, "medium": 0.85, "low": 0.65}
EXPLOITABILITY_WEIGHTS = {"high": 1.12, "moderate": 1.0, "low": 0.88}


def severity_from_score(score):
    if score >= 85:
        return "critical"
    if score >= 70:
        return "high"
    if score >= 45:
        return "medium"
    if score >= 20:
        return "low"
    return "informational"


def assess(finding):
    base_severity = finding.get("base_severity", finding.get("severity", "low"))
    base = BASE_WEIGHTS.get(base_severity, BASE_WEIGHTS["low"])
    confidence = finding.get("confidence", "medium")
    conf_weight = CONFIDENCE_WEIGHTS.get(confidence, 0.85)
    exploitability = finding.get("exploitability", "low")
    exp_weight = EXPLOITABILITY_WEIGHTS.get(exploitability, 0.88)
    endpoints = max(1, int(finding.get("affected_endpoints", 1) or 1))
    endpoint_factor = 1 + min(0.06 * (endpoints - 1), 0.24)
    weaknesses = max(0, int(finding.get("weakness_count", 0) or 0))
    weakness_factor = 1 + min(0.04 * weaknesses, 0.2)

    raw = base * conf_weight * exp_weight * endpoint_factor * weakness_factor
    score = round(max(0.0, min(100.0, raw)), 1)
    severity = severity_from_score(score)

    reasoning = [
        f"Base weight for '{base_severity}' severity: {base:.0f}/100.",
        f"Confidence '{confidence}' multiplies the base by {conf_weight:.2f}.",
        f"Exploitability '{exploitability}' multiplies the result by {exp_weight:.2f}.",
        f"{endpoints} affected endpoint(s) apply a {endpoint_factor:.2f}x scope factor.",
        f"{weaknesses} supporting configuration weakness(es) apply a {weakness_factor:.2f}x factor.",
        f"Final score {score:.1f}/100 maps to '{severity}' on the documented thresholds (85/70/45/20).",
    ]
    if not finding.get("verified", True):
        reasoning.append("Finding is an unverified indicator, so its confidence reduces the final score.")

    model_source = "rule-based-transparent"
    model = get_model()
    if Config.USE_SYNTHETIC_ML and model.available:
        prediction = model.predict([base, conf_weight, exp_weight, endpoint_factor, weakness_factor])
        if prediction:
            reasoning.append(
                f"Synthetic-data ML classifier suggestion: '{prediction}' (demonstration only; the transparent score above is authoritative)."
            )
            model_source = "synthetic-ml-assisted-rule-based"

    return {
        "severity": severity,
        "risk_score": score,
        "confidence": confidence,
        "exploitability": exploitability,
        "model_source": model_source,
        "reasoning": reasoning,
        "components": {
            "base_weight": base,
            "confidence_weight": conf_weight,
            "exploitability_weight": exp_weight,
            "endpoint_factor": round(endpoint_factor, 2),
            "weakness_factor": round(weakness_factor, 2),
        },
    }

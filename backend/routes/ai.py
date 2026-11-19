from flask import Blueprint, jsonify

from ai_engine.explainer import explain, summarize
from models.scan import Scan
from models.vulnerability import Vulnerability
from risk_assessment.engine import BASE_WEIGHTS, CONFIDENCE_WEIGHTS, EXPLOITABILITY_WEIGHTS, severity_from_score
from risk_assessment.ml_model import get_model
from routes.deps import db_session, json_body, require_auth
from scanners.zap import zap_status

ai_bp = Blueprint("ai", __name__, url_prefix="/api/ai")


@ai_bp.get("/model")
@require_auth
def model_info():
    model = get_model()
    return jsonify(
        {
            "model": model.info(),
            "explanation_source": "local-knowledge-based-generator",
            "external_ai_required": False,
            "zap": zap_status(),
            "scoring_model": {
                "type": "transparent weighted rules",
                "base_weights": BASE_WEIGHTS,
                "confidence_weights": CONFIDENCE_WEIGHTS,
                "exploitability_weights": EXPLOITABILITY_WEIGHTS,
                "severity_thresholds": {"critical": 85, "high": 70, "medium": 45, "low": 20},
            },
        }
    )


@ai_bp.get("/assessment/<scan_id>")
@require_auth
def assessment(scan_id):
    from flask import g

    with db_session() as db:
        scan = db.query(Scan).filter(Scan.id == scan_id, Scan.user_id == g.user_id).first()
        if scan is None:
            return jsonify({"error": "Scan not found"}), 404
        findings = [item.to_dict() for item in scan.vulnerabilities]
        result = summarize(scan, findings)
        result.update(
            {
                "scan_id": scan.id,
                "target_url": scan.target_url,
                "scan_status": scan.status,
                "model": get_model().info(),
                "findings": [
                    {
                        "id": item["id"],
                        "name": item["name"],
                        "severity": item["severity"],
                        "risk_score": item["risk_score"],
                        "confidence": item["confidence"],
                        "reasoning": item["reasoning"],
                        "model_source": item["model_source"],
                    }
                    for item in findings
                ],
            }
        )
        return jsonify({"assessment": result})


@ai_bp.get("/validation/<scan_id>")
@require_auth
def validation(scan_id):
    from flask import g

    with db_session() as db:
        scan = db.query(Scan).filter(Scan.id == scan_id, Scan.user_id == g.user_id).first()
        if scan is None:
            return jsonify({"error": "Scan not found"}), 404
        findings = db.query(Vulnerability).filter(Vulnerability.scan_id == scan_id).all()
        confidence = {}
        for item in findings:
            confidence[item.confidence] = confidence.get(item.confidence, 0) + 1
        return jsonify(
            {
                "scan_id": scan_id,
                "total_findings": len(findings),
                "verified_findings": sum(1 for item in findings if item.verified),
                "potential_indicators": sum(1 for item in findings if not item.verified),
                "confidence_distribution": confidence,
                "evidence_coverage": sum(1 for item in findings if bool(item.evidence)),
                "duplicate_groups_removed": max(0, len(findings) - len({(item.name, item.category) for item in findings})),
                "method": "Evidence required, duplicate keys merged, benign probes labelled as potential, unsupported claims discarded.",
            }
        )


@ai_bp.post("/explain")
@require_auth
def explain_finding():
    data = json_body()
    if not data.get("name") and not data.get("category"):
        return jsonify({"error": "Provide a name or category to explain"}), 400
    result = explain(
        {
            "key": str(data.get("key", "")),
            "category": str(data.get("category", "")),
            "recommendation": str(data.get("recommendation", "")),
        }
    )
    return jsonify({"explanation": result})


@ai_bp.get("/score-guide")
@require_auth
def score_guide():
    examples = []
    for severity, score in [("critical", 92), ("high", 76), ("medium", 52), ("low", 26), ("informational", 10)]:
        examples.append(
            {
                "severity": severity,
                "base_score": score,
                "result_after_high_confidence": severity_from_score(score * 0.88),
            }
        )
    return jsonify({"examples": examples})

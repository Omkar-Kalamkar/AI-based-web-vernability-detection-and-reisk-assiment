from flask import Blueprint, jsonify, request

from models.scan import Scan
from models.vulnerability import Vulnerability
from routes.deps import db_session, json_body, require_auth

vulnerabilities_bp = Blueprint("vulnerabilities", __name__, url_prefix="/api/vulnerabilities")

ALLOWED_STATUS = {"open", "in_progress", "resolved", "false_positive", "accepted"}


@vulnerabilities_bp.get("")
@require_auth
def list_vulnerabilities():
    from flask import g

    severity = request.args.get("severity", "").lower()
    status = request.args.get("status", "").lower()
    search = request.args.get("search", "").strip().lower()
    scan_id = request.args.get("scan_id", "").strip()
    try:
        limit = max(1, min(int(request.args.get("limit", 200)), 500))
    except (TypeError, ValueError):
        limit = 200

    with db_session() as db:
        query = db.query(Vulnerability).join(Scan).filter(Scan.user_id == g.user_id)
        if scan_id:
            query = query.filter(Vulnerability.scan_id == scan_id)
        if severity and severity != "all":
            query = query.filter(Vulnerability.severity == severity)
        if status and status != "all":
            query = query.filter(Vulnerability.status == status)
        if search:
            query = query.filter(
                Vulnerability.name.ilike(f"%{search}%") | Vulnerability.category.ilike(f"%{search}%")
            )
        total = query.count()
        findings = query.order_by(Vulnerability.risk_score.desc()).limit(limit).all()
        return jsonify({"vulnerabilities": [item.to_dict() for item in findings], "total": total})


@vulnerabilities_bp.get("/summary")
@require_auth
def vulnerability_summary():
    from flask import g

    with db_session() as db:
        items = (
            db.query(Vulnerability)
            .join(Scan)
            .filter(Scan.user_id == g.user_id)
            .all()
        )
        by_severity = {}
        by_status = {}
        by_category = {}
        for item in items:
            by_severity[item.severity] = by_severity.get(item.severity, 0) + 1
            by_status[item.status] = by_status.get(item.status, 0) + 1
            by_category[item.category] = by_category.get(item.category, 0) + 1
        return jsonify(
            {
                "total": len(items),
                "by_severity": by_severity,
                "by_status": by_status,
                "by_category": by_category,
                "open_count": sum(1 for item in items if item.status == "open"),
            }
        )


@vulnerabilities_bp.get("/<finding_id>")
@require_auth
def get_vulnerability(finding_id):
    from flask import g

    with db_session() as db:
        item = (
            db.query(Vulnerability)
            .join(Scan)
            .filter(Vulnerability.id == finding_id, Scan.user_id == g.user_id)
            .first()
        )
        if item is None:
            return jsonify({"error": "Vulnerability not found"}), 404
        return jsonify({"vulnerability": item.to_dict()})


@vulnerabilities_bp.patch("/<finding_id>")
@require_auth
def update_vulnerability(finding_id):
    from flask import g

    data = json_body()
    status = str(data.get("status", "")).lower()
    if status not in ALLOWED_STATUS:
        return jsonify({"error": f"Status must be one of: {', '.join(sorted(ALLOWED_STATUS))}"}), 400
    with db_session() as db:
        item = (
            db.query(Vulnerability)
            .join(Scan)
            .filter(Vulnerability.id == finding_id, Scan.user_id == g.user_id)
            .first()
        )
        if item is None:
            return jsonify({"error": "Vulnerability not found"}), 404
        item.status = status
        db.commit()
        return jsonify({"vulnerability": item.to_dict()})

import secrets
from datetime import datetime

from flask import Blueprint, jsonify, request

from database import SessionLocal
from models.scan import Scan
from models.user import utcnow
from routes.deps import db_session, json_body, require_auth, scan_rate_limited
from scanners.safe_scanner import start_scan_worker
from scanners.url_guard import TargetValidationError, validate_target

scans_bp = Blueprint("scans", __name__, url_prefix="/api/scans")


def _owned_scan(db, scan_id, user_id):
    return db.query(Scan).filter(Scan.id == scan_id, Scan.user_id == user_id).first()


@scans_bp.post("")
@require_auth
def create_scan():
    from flask import g

    data = json_body()
    target_url = str(data.get("target_url", "")).strip()
    if not target_url:
        return jsonify({"error": "Target URL is required"}), 400
    if data.get("authorization_confirmed") is not True:
        return jsonify({"error": "You must confirm that you own or are authorized to test this target"}), 403

    try:
        target = validate_target(target_url)
    except TargetValidationError as exc:
        return jsonify({"error": str(exc)}), 400

    with db_session() as db:
        if scan_rate_limited(db, g.user_id):
            return jsonify({"error": "Scan rate limit reached. Please try again later."}), 429
        scan = Scan(
            id="scan_" + secrets.token_hex(10),
            user_id=g.user_id,
            target_url=target["url"],
            target_host=target["host"],
            status="queued",
            progress=0,
            stage="Queued",
            scan_mode="passive-safe",
        )
        db.add(scan)
        db.commit()
        db.refresh(scan)
        result = scan.to_dict()

    start_scan_worker(scan.id)
    return jsonify({"scan": result, "message": "Scan started. Poll /api/scans/<id> for progress."}), 202


@scans_bp.get("")
@require_auth
def list_scans():
    from flask import g

    try:
        limit = max(1, min(int(request.args.get("limit", 50)), 200))
    except (TypeError, ValueError):
        limit = 50
    with db_session() as db:
        scans = (
            db.query(Scan)
            .filter(Scan.user_id == g.user_id)
            .order_by(Scan.created_at.desc())
            .limit(limit)
            .all()
        )
        return jsonify({"scans": [scan.to_dict() for scan in scans], "total": len(scans)})


@scans_bp.get("/<scan_id>")
@require_auth
def get_scan(scan_id):
    from flask import g

    with db_session() as db:
        scan = _owned_scan(db, scan_id, g.user_id)
        if scan is None:
            return jsonify({"error": "Scan not found"}), 404
        return jsonify({"scan": scan.to_dict(include_findings=True)})


@scans_bp.delete("/<scan_id>")
@require_auth
def delete_scan(scan_id):
    from flask import g

    with db_session() as db:
        scan = _owned_scan(db, scan_id, g.user_id)
        if scan is None:
            return jsonify({"error": "Scan not found"}), 404
        db.delete(scan)
        db.commit()
        return jsonify({"message": "Scan and its findings were deleted"})


@scans_bp.post("/<scan_id>/retry")
@require_auth
def retry_scan(scan_id):
    from flask import g

    with db_session() as db:
        scan = _owned_scan(db, scan_id, g.user_id)
        if scan is None:
            return jsonify({"error": "Scan not found"}), 404
        try:
            validate_target(scan.target_url)
        except TargetValidationError as exc:
            return jsonify({"error": str(exc)}), 400
        if scan_rate_limited(db, g.user_id):
            return jsonify({"error": "Scan rate limit reached. Please try again later."}), 429
        for vulnerability in scan.vulnerabilities:
            db.delete(vulnerability)
        scan.status = "queued"
        scan.progress = 0
        scan.stage = "Queued"
        scan.error = None
        scan.security_score = 100
        scan.total_findings = 0
        scan.critical_count = 0
        scan.high_count = 0
        scan.medium_count = 0
        scan.low_count = 0
        scan.info_count = 0
        scan.started_at = None
        scan.completed_at = None
        scan.created_at = utcnow()
        db.commit()
        result = scan.to_dict()

    start_scan_worker(scan_id)
    return jsonify({"scan": result, "message": "Scan restarted"}), 202

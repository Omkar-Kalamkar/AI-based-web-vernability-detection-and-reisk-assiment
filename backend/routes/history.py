from datetime import timedelta

from flask import Blueprint, jsonify, request

from models.scan import Scan
from models.user import utcnow
from routes.deps import db_session, require_auth

history_bp = Blueprint("history", __name__, url_prefix="/api/history")


@history_bp.get("")
@require_auth
def list_history():
    from flask import g

    try:
        limit = max(1, min(int(request.args.get("limit", 100)), 500))
    except (TypeError, ValueError):
        limit = 100
    with db_session() as db:
        scans = db.query(Scan).filter(Scan.user_id == g.user_id).order_by(Scan.created_at.desc()).limit(limit).all()
        ordered = sorted(scans, key=lambda item: item.created_at)
        previous_by_id = {}
        last_for_target = {}
        for item in ordered:
            previous = last_for_target.get(item.target_url)
            if previous is not None:
                previous_by_id[item.id] = previous
            last_for_target[item.target_url] = item.security_score
        result = []
        for item in scans:
            previous = previous_by_id.get(item.id)
            result.append(
                {
                    **item.to_dict(),
                    "previous_score": previous,
                    "score_change": None if previous is None else item.security_score - previous,
                }
            )
        return jsonify({"history": result, "total": len(scans)})


@history_bp.get("/stats")
@require_auth
def dashboard_stats():
    from flask import g

    with db_session() as db:
        scans = db.query(Scan).filter(Scan.user_id == g.user_id).order_by(Scan.created_at.asc()).all()
        total_scans = len(scans)
        completed = [item for item in scans if item.status == "completed"]
        totals = {
            "total_scans": total_scans,
            "completed_scans": len(completed),
            "running_scans": sum(1 for item in scans if item.status in {"queued", "running"}),
            "failed_scans": sum(1 for item in scans if item.status == "failed"),
            "total_vulnerabilities": sum(item.total_findings for item in scans),
            "critical": sum(item.critical_count for item in scans),
            "high": sum(item.high_count for item in scans),
            "medium": sum(item.medium_count for item in scans),
            "low": sum(item.low_count for item in scans),
            "informational": sum(item.info_count for item in scans),
            "average_score": round(sum(item.security_score for item in completed) / len(completed), 1) if completed else 100,
            "latest_score": completed[-1].security_score if completed else None,
        }
        severity = [
            {"name": "Critical", "value": totals["critical"]},
            {"name": "High", "value": totals["high"]},
            {"name": "Medium", "value": totals["medium"]},
            {"name": "Low", "value": totals["low"]},
            {"name": "Informational", "value": totals["informational"]},
        ]
        trend = [
            {
                "date": item.created_at.strftime("%b %d") if item.created_at else "",
                "score": item.security_score,
                "scan_id": item.id,
                "target": item.target_host,
            }
            for item in completed[-10:]
        ]
        activity_map = {}
        for item in scans:
            key = item.created_at.strftime("%Y-%m-%d") if item.created_at else ""
            activity_map[key] = activity_map.get(key, 0) + 1
        activity = []
        today = utcnow().date()
        for offset in range(13, -1, -1):
            day = today - timedelta(days=offset)
            key = day.isoformat()
            activity.append({"date": day.strftime("%b %d"), "scans": activity_map.get(key, 0)})
        recent = [item.to_dict() for item in scans[:6]]
        return jsonify(
            {
                "stats": totals,
                "severity_distribution": severity,
                "score_trend": trend,
                "activity": activity,
                "recent_scans": recent,
            }
        )


@history_bp.delete("")
@require_auth
def clear_history():
    from flask import g

    with db_session() as db:
        scans = db.query(Scan).filter(Scan.user_id == g.user_id).all()
        for item in scans:
            db.delete(item)
        db.commit()
        return jsonify({"message": f"Deleted {len(scans)} scan(s)"})


@history_bp.delete("/<scan_id>")
@require_auth
def delete_history_item(scan_id):
    from flask import g

    with db_session() as db:
        scan = db.query(Scan).filter(Scan.id == scan_id, Scan.user_id == g.user_id).first()
        if scan is None:
            return jsonify({"error": "Scan not found"}), 404
        db.delete(scan)
        db.commit()
        return jsonify({"message": "Scan deleted"})

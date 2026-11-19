from flask import Blueprint, jsonify, send_file

from models.scan import Scan
from report_generator.csv_report import build_csv
from report_generator.pdf_report import build_pdf
from routes.deps import db_session, require_auth

reports_bp = Blueprint("reports", __name__, url_prefix="/api/reports")


def _load_scan(scan_id):
    from flask import g

    db = db_session().__enter__()
    try:
        scan = db.query(Scan).filter(Scan.id == scan_id, Scan.user_id == g.user_id).first()
        if scan is None:
            return None, None
        findings = sorted(scan.vulnerabilities, key=lambda item: -item.risk_score)
        return scan, findings
    finally:
        db.close()


def _download_response(data, filename, mimetype):
    from io import BytesIO

    return send_file(
        BytesIO(data),
        mimetype=mimetype,
        as_attachment=True,
        download_name=filename,
    )


@reports_bp.get("/<scan_id>/pdf")
@require_auth
def pdf_report(scan_id):
    scan, findings = _load_scan(scan_id)
    if scan is None:
        return jsonify({"error": "Scan not found"}), 404
    data = build_pdf(scan, findings)
    return _download_response(data, f"secureai-report-{scan.target_host}-{scan.id[:12]}.pdf", "application/pdf")


@reports_bp.get("/<scan_id>/csv")
@require_auth
def csv_report(scan_id):
    scan, findings = _load_scan(scan_id)
    if scan is None:
        return jsonify({"error": "Scan not found"}), 404
    data = build_csv(scan, findings)
    return _download_response(data, f"secureai-report-{scan.target_host}-{scan.id[:12]}.csv", "text/csv")


@reports_bp.get("/<scan_id>/preview")
@require_auth
def report_preview(scan_id):
    scan, findings = _load_scan(scan_id)
    if scan is None:
        return jsonify({"error": "Scan not found"}), 404
    return jsonify(
        {
            "scan": scan.to_dict(),
            "finding_count": len(findings),
            "has_remediation": all(bool(item.recommendation) for item in findings),
            "formats": ["pdf", "csv"],
        }
    )

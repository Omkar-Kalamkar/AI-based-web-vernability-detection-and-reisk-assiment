"""CSV report generation for a completed scan."""

import csv
import io

FIELDS = [
    ("id", "Finding ID"),
    ("name", "Vulnerability"),
    ("category", "Category"),
    ("severity", "Severity"),
    ("risk_score", "Risk Score"),
    ("confidence", "Confidence"),
    ("verified", "Verified"),
    ("affected_url", "Affected URL"),
    ("description", "Description"),
    ("impact", "Potential Impact"),
    ("evidence", "Evidence"),
    ("recommendation", "Recommended Solution"),
    ("simple_explanation", "Simple Explanation"),
    ("why_dangerous", "Why Dangerous"),
    ("secure_coding", "Secure Coding Practice"),
    ("prevention", "Prevention"),
    ("references", "References"),
    ("affected_endpoints", "Affected Endpoints"),
    ("exploitability", "Exploitability"),
    ("model_source", "Risk Model"),
    ("reasoning", "Risk Reasoning"),
    ("status", "Status"),
]


def build_csv(scan, vulnerabilities):
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["SecureAI Security Report"])
    writer.writerow(["Scan ID", scan.id])
    writer.writerow(["Target URL", scan.target_url])
    writer.writerow(["Scan Mode", scan.scan_mode])
    writer.writerow(["Created At", scan.created_at.isoformat() if scan.created_at else ""])
    writer.writerow(["Completed At", scan.completed_at.isoformat() if scan.completed_at else ""])
    writer.writerow(["Security Score", scan.security_score])
    writer.writerow(["Total Findings", scan.total_findings])
    writer.writerow(
        [
            "Severity Distribution",
            f"critical={scan.critical_count}, high={scan.high_count}, medium={scan.medium_count}, low={scan.low_count}, informational={scan.info_count}",
        ]
    )
    writer.writerow([])
    writer.writerow([label for _key, label in FIELDS])
    for vuln in vulnerabilities:
        data = vuln.to_dict()
        writer.writerow([", ".join(map(str, data[key])) if key in ("references", "reasoning") else data[key] for key, _label in FIELDS])
    output.seek(0)
    return output.getvalue().encode("utf-8-sig")

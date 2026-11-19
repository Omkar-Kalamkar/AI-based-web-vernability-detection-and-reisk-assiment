from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from database import Base
from models.user import utcnow


class Scan(Base):
    __tablename__ = "scans"

    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    target_url = Column(String(2048), nullable=False)
    target_host = Column(String(255), nullable=False)
    status = Column(String(32), default="queued", nullable=False, index=True)
    progress = Column(Integer, default=0, nullable=False)
    stage = Column(String(255), default="Queued", nullable=False)
    pages_scanned = Column(Integer, default=0, nullable=False)
    security_score = Column(Integer, default=100, nullable=False)
    total_findings = Column(Integer, default=0, nullable=False)
    critical_count = Column(Integer, default=0, nullable=False)
    high_count = Column(Integer, default=0, nullable=False)
    medium_count = Column(Integer, default=0, nullable=False)
    low_count = Column(Integer, default=0, nullable=False)
    info_count = Column(Integer, default=0, nullable=False)
    scan_mode = Column(String(64), default="passive-safe", nullable=False)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    owner = relationship("User", back_populates="scans")
    vulnerabilities = relationship("Vulnerability", back_populates="scan", cascade="all, delete-orphan")

    def to_dict(self, include_findings=False):
        data = {
            "id": self.id,
            "target_url": self.target_url,
            "target_host": self.target_host,
            "status": self.status,
            "progress": self.progress,
            "stage": self.stage,
            "pages_scanned": self.pages_scanned,
            "security_score": self.security_score,
            "total_findings": self.total_findings,
            "severity_counts": {
                "critical": self.critical_count,
                "high": self.high_count,
                "medium": self.medium_count,
                "low": self.low_count,
                "informational": self.info_count,
            },
            "scan_mode": self.scan_mode,
            "error": self.error,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
        if include_findings:
            data["vulnerabilities"] = [v.to_dict() for v in sorted(self.vulnerabilities, key=lambda x: -x.risk_score)]
        return data

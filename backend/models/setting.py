from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base
from models.user import utcnow


class UserSetting(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    theme = Column(String(32), default="dark", nullable=False)
    notifications = Column(Integer, default=1, nullable=False)
    auto_refresh = Column(Integer, default=1, nullable=False)
    default_max_pages = Column(Integer, default=8, nullable=False)
    risk_sensitivity = Column(String(32), default="balanced", nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    user = relationship("User")

    def to_dict(self):
        return {
            "theme": self.theme,
            "notifications": bool(self.notifications),
            "auto_refresh": bool(self.auto_refresh),
            "default_max_pages": self.default_max_pages,
            "risk_sensitivity": self.risk_sensitivity,
        }

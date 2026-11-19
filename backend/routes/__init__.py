"""REST API blueprints."""

from .auth import auth_bp  # noqa: F401
from .scans import scans_bp  # noqa: F401
from .vulnerabilities import vulnerabilities_bp  # noqa: F401
from .ai import ai_bp  # noqa: F401
from .reports import reports_bp  # noqa: F401
from .history import history_bp  # noqa: F401
from .settings import settings_bp  # noqa: F401

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def _bool_env(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _list_env(name, default=""):
    return [item.strip().lower() for item in os.getenv(name, default).split(",") if item.strip()]


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "secureai-dev-secret-change-me")
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'data' / 'secureai.db'}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    FRONTEND_ORIGINS = _list_env(
        "FRONTEND_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174",
    )

    LOCAL_LAB_MODE = _bool_env("LOCAL_LAB_MODE", True)
    ALLOWED_LAB_HOSTS = _list_env("ALLOWED_LAB_HOSTS", "localhost,127.0.0.1,::1,test.local,dvwa.local,juice-shop.local")
    ALLOWED_LAB_PORTS = [int(p) for p in _list_env("ALLOWED_LAB_PORTS", "3000,3001,5000,8000,8001,8080,8081,8090,8888") if p.isdigit()]
    ALLOW_EXTERNAL_TARGETS = _bool_env("ALLOW_EXTERNAL_TARGETS", False)
    PUBLIC_TARGET_ALLOWLIST = _list_env("PUBLIC_TARGET_ALLOWLIST", "")

    SCAN_CONNECT_TIMEOUT = float(os.getenv("SCAN_CONNECT_TIMEOUT", "3"))
    SCAN_READ_TIMEOUT = float(os.getenv("SCAN_READ_TIMEOUT", "8"))
    MAX_RESPONSE_BYTES = int(os.getenv("MAX_RESPONSE_BYTES", "1048576"))
    MAX_PAGES_PER_SCAN = int(os.getenv("MAX_PAGES_PER_SCAN", "8"))
    MAX_REDIRECTS = 3
    SCAN_RATE_LIMIT_PER_HOUR = int(os.getenv("SCAN_RATE_LIMIT_PER_HOUR", "20"))
    TOKEN_TTL_HOURS = int(os.getenv("TOKEN_TTL_HOURS", "24"))

    USE_SYNTHETIC_ML = _bool_env("USE_SYNTHETIC_ML", False)
    OWASP_ZAP_URL = os.getenv("OWASP_ZAP_URL", "")
    OWASP_ZAP_API_KEY = os.getenv("OWASP_ZAP_API_KEY", "")

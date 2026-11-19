"""Shared dependency helpers for API routes."""

import hashlib
import re
from contextlib import contextmanager
from datetime import timedelta
from functools import wraps

from flask import g, jsonify, request

from config import Config
from database import SessionLocal
from models.session import AuthSession
from models.user import utcnow

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


@contextmanager
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_token(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def current_user_id():
    return getattr(g, "user_id", None)


def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        token = header[7:].strip() if header.lower().startswith("bearer ") else request.cookies.get("secureai_session")
        if not token:
            return jsonify({"error": "Authentication required"}), 401
        with db_session() as db:
            auth = (
                db.query(AuthSession)
                .filter(AuthSession.token_hash == hash_token(token), AuthSession.revoked == 0)
                .first()
            )
            if auth is None or auth.expires_at <= utcnow():
                return jsonify({"error": "Session expired or invalid"}), 401
            g.user_id = auth.user_id
            g.auth_session_id = auth.id
        return fn(*args, **kwargs)

    return wrapper


def json_body():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def valid_email(value):
    return isinstance(value, str) and len(value) <= 255 and bool(EMAIL_RE.match(value.strip()))


def scan_rate_limited(db, user_id):
    from models.scan import Scan

    since = utcnow() - timedelta(hours=1)
    count = db.query(Scan).filter(Scan.user_id == user_id, Scan.created_at >= since).count()
    return count >= Config.SCAN_RATE_LIMIT_PER_HOUR

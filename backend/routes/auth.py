import re
from datetime import timedelta

from flask import Blueprint, jsonify, make_response, request
from werkzeug.security import check_password_hash, generate_password_hash

from config import Config
from database import SessionLocal
from models.session import AuthSession
from models.user import User, utcnow
from routes.deps import db_session, hash_token, json_body, require_auth, valid_email

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{3,60}$")


def _create_session(db, user_id):
    import secrets

    token = secrets.token_urlsafe(36)
    session = AuthSession(
        user_id=user_id,
        token_hash=hash_token(token),
        created_at=utcnow(),
        expires_at=utcnow() + timedelta(hours=Config.TOKEN_TTL_HOURS),
    )
    db.add(session)
    db.commit()
    return token


def _auth_response(user, token, status=200):
    response = make_response(
        jsonify({"token": token, "user": user.to_dict(), "expires_in_hours": Config.TOKEN_TTL_HOURS}),
        status,
    )
    response.set_cookie(
        "secureai_session",
        token,
        httponly=True,
        samesite="Lax",
        secure=request.is_secure,
        max_age=Config.TOKEN_TTL_HOURS * 3600,
        path="/",
    )
    return response


@auth_bp.post("/register")
def register():
    data = json_body()
    username = str(data.get("username", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = data.get("password", "")

    if not USERNAME_RE.match(username):
        return jsonify({"error": "Username must be 3-60 characters using letters, numbers, dots, dashes or underscores"}), 400
    if not valid_email(email):
        return jsonify({"error": "A valid email address is required"}), 400
    if not isinstance(password, str) or len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters long"}), 400

    with db_session() as db:
        if db.query(User).filter(User.email == email).first():
            return jsonify({"error": "An account with this email already exists"}), 409
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password, method="scrypt"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        token = _create_session(db, user.id)
        return _auth_response(user, token, 201)


@auth_bp.post("/login")
def login():
    data = json_body()
    email = str(data.get("email", "")).strip().lower()
    password = data.get("password", "")
    if not email or not isinstance(password, str):
        return jsonify({"error": "Email and password are required"}), 400

    with db_session() as db:
        user = db.query(User).filter(User.email == email).first()
        if user is None or not check_password_hash(user.password_hash, password):
            return jsonify({"error": "Invalid email or password"}), 401
        token = _create_session(db, user.id)
        return _auth_response(user, token)


@auth_bp.get("/me")
@require_auth
def me():
    from flask import g

    with db_session() as db:
        user = db.query(User).filter(User.id == g.user_id).first()
        if user is None:
            return jsonify({"error": "User not found"}), 404
        return jsonify({"user": user.to_dict()})


@auth_bp.post("/logout")
@require_auth
def logout():
    from flask import g

    header = request.headers.get("Authorization", "")
    token = header[7:].strip() if header.lower().startswith("bearer ") else request.cookies.get("secureai_session")
    with db_session() as db:
        auth = db.query(AuthSession).filter(AuthSession.token_hash == hash_token(token)).first()
        if auth:
            auth.revoked = 1
            db.commit()
    response = make_response(jsonify({"message": "Logged out successfully"}))
    response.delete_cookie("secureai_session", path="/")
    return response


def seed_demo_user():
    with SessionLocal() as db:
        existing = db.query(User).filter(User.email == "demo@secureai.local").first()
        if existing:
            return
        db.add(
            User(
                username="demo",
                email="demo@secureai.local",
                password_hash=generate_password_hash("Demo@12345", method="scrypt"),
            )
        )
        db.commit()

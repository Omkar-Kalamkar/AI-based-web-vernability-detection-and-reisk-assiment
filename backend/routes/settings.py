from flask import Blueprint, jsonify

from config import Config
from models.setting import UserSetting
from routes.deps import db_session, json_body, require_auth

settings_bp = Blueprint("settings", __name__, url_prefix="/api/settings")

ALLOWED = {
    "theme": lambda value: value in {"dark", "light"},
    "notifications": lambda value: isinstance(value, bool),
    "auto_refresh": lambda value: isinstance(value, bool),
    "default_max_pages": lambda value: isinstance(value, int) and 1 <= value <= 20,
    "risk_sensitivity": lambda value: value in {"conservative", "balanced", "aggressive"},
}


def _get_or_create(db, user_id):
    setting = db.query(UserSetting).filter(UserSetting.user_id == user_id).first()
    if setting is None:
        setting = UserSetting(user_id=user_id)
        db.add(setting)
        db.commit()
        db.refresh(setting)
    return setting


@settings_bp.get("")
@require_auth
def get_settings():
    from flask import g

    with db_session() as db:
        return jsonify({"settings": _get_or_create(db, g.user_id).to_dict()})


@settings_bp.put("")
@require_auth
def update_settings():
    from flask import g

    data = json_body()
    for key, value in data.items():
        if key in ALLOWED and not ALLOWED[key](value):
            return jsonify({"error": f"Invalid value for {key}"}), 400
    with db_session() as db:
        setting = _get_or_create(db, g.user_id)
        for key, value in data.items():
            if key not in ALLOWED:
                continue
            if isinstance(value, bool):
                value = 1 if value else 0
            setattr(setting, key, value)
        db.commit()
        return jsonify({"settings": setting.to_dict(), "message": "Settings saved"})


@settings_bp.get("/platform")
@require_auth
def platform_settings():
    return jsonify(
        {
            "platform": {
                "local_lab_mode": Config.LOCAL_LAB_MODE,
                "allowed_lab_hosts": Config.ALLOWED_LAB_HOSTS,
                "allowed_lab_ports": Config.ALLOWED_LAB_PORTS,
                "external_targets_allowed": Config.ALLOW_EXTERNAL_TARGETS,
                "scan_connect_timeout": Config.SCAN_CONNECT_TIMEOUT,
                "scan_read_timeout": Config.SCAN_READ_TIMEOUT,
                "max_pages_per_scan": Config.MAX_PAGES_PER_SCAN,
                "scan_rate_limit_per_hour": Config.SCAN_RATE_LIMIT_PER_HOUR,
            },
            "note": "Server-side scanning limits are configured through environment variables by the administrator.",
        }
    )

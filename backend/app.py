from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS

load_dotenv()

from config import Config


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = Config.SECRET_KEY
    app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024
    CORS(app, origins=Config.FRONTEND_ORIGINS, supports_credentials=True)

    from database import init_db
    init_db()

    from routes.auth import auth_bp
    from routes.scans import scans_bp
    from routes.vulnerabilities import vulnerabilities_bp
    from routes.ai import ai_bp
    from routes.reports import reports_bp
    from routes.history import history_bp
    from routes.settings import settings_bp

    for blueprint in (auth_bp, scans_bp, vulnerabilities_bp, ai_bp, reports_bp, history_bp, settings_bp):
        app.register_blueprint(blueprint)

    from routes.auth import seed_demo_user
    seed_demo_user()

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "service": "SecureAI", "lab_mode": Config.LOCAL_LAB_MODE})

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(_error):
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(413)
    def too_large(_error):
        return jsonify({"error": "Request payload too large"}), 413

    @app.errorhandler(500)
    def server_error(_error):
        return jsonify({"error": "Internal server error"}), 500

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000, threaded=True, debug=False)

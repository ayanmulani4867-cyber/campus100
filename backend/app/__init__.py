import os
import logging
from pathlib import Path
from flask import Flask, send_from_directory
from config import config_by_name
from app.extensions import db, migrate
from app.utils.errors import register_error_handlers
from app.routes import register_blueprints


def create_app(config_name=None):
    config_name = config_name or os.environ.get("FLASK_ENV", "production")
    config_class = config_by_name.get(config_name, config_by_name["production"])

    frontend_dir = os.environ.get(
        "FRONTEND_DIR",
        getattr(config_class, "FRONTEND_DIR", str(Path(__file__).resolve().parent.parent.parent / "frontend"))
    )

    app = Flask(
        __name__,
        static_folder=frontend_dir if os.path.isdir(frontend_dir) else None,
        static_url_path="",
    )
    app.config.from_object(config_class)

    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        app.logger.warning(
            "DATABASE_URL is not set. The app will start, but database operations will fail."
        )

    logging.basicConfig(level=logging.INFO if not app.debug else logging.DEBUG)

    db.init_app(app)
    migrate.init_app(app, db)

    from app import models  # noqa: F401

    # Keep database schema compatible without destroying data
    if app.config.get("SQLALCHEMY_DATABASE_URI"):
        from app.schema_compat import ensure_schema_compatibility
        with app.app_context():
            try:
                ensure_schema_compatibility()
            except Exception:
                app.logger.exception("Schema compatibility check failed")

    register_error_handlers(app)
    register_blueprints(app)

    from flask_cors import CORS
    cors_origins = app.config.get("CORS_ORIGINS")
    if cors_origins:
        CORS(app, supports_credentials=True, origins=cors_origins, allow_headers=["Content-Type", "X-Session-Token", "Authorization"])
    else:
        CORS(app, supports_credentials=True, origins=r".*", allow_headers=["Content-Type", "X-Session-Token", "Authorization"])

    @app.get("/api/health")
    def health():
        db_configured = bool(app.config.get("SQLALCHEMY_DATABASE_URI"))
        return {
            "success": True,
            "status": "ok",
            "environment": config_name,
            "databaseConfigured": db_configured
        }

    # Serve the frontend as static files so the whole project runs as one web service
    if app.static_folder and os.path.isdir(app.static_folder):
        @app.get("/")
        def index():
            return send_from_directory(app.static_folder, "index.html")

        @app.get("/<path:filename>")
        def static_files(filename):
            full_path = os.path.join(app.static_folder, filename)
            if os.path.isfile(full_path):
                return send_from_directory(app.static_folder, filename)
            # Unknown path: fallback to index.html so client routes work
            return send_from_directory(app.static_folder, "index.html")

    return app

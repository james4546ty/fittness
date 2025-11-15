import os
from datetime import timedelta
from flask import Flask
from extensions import db, login_manager, csrf

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")

    # Core configuration
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-this-secret-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///fitness_tracker.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Security: session cookie settings
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    # Only secure cookies if running over HTTPS
    app.config["SESSION_COOKIE_SECURE"] = bool(os.getenv("SESSION_COOKIE_SECURE", "0") in {"1", "true", "True"})

    # Uploads (served from static/uploads)
    app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"
    login_manager.remember_cookie_duration = timedelta(days=30)

    # Ensure upload folder exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.workouts import workouts_bp
    from routes.nutrition import nutrition_bp
    from routes.metrics import metrics_bp
    from routes.goals import goals_bp
    from routes.dashboard import dashboard_bp
    from routes.extras import extras_bp
    from routes.export import export_bp
    from routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(workouts_bp)
    app.register_blueprint(nutrition_bp)
    app.register_blueprint(metrics_bp)
    app.register_blueprint(goals_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(extras_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(api_bp)

    # Create database tables if they do not exist
    with app.app_context():
        from models import User  # ensure models are imported
        db.create_all()

    # Root route
    from flask import redirect, url_for
    from flask_login import current_user
    @app.route("/")
    def home():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard.index"))
        return redirect(url_for("auth.login"))

    return app


# WSGI entry point
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
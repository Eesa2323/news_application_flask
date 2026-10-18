from pathlib import Path

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

# Extensions get created up here so we can import them elsewhere without
# triggering circular imports. db handles our database, login_manager keeps
# track of who's logged in.
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev-change-this-key",
        SQLALCHEMY_DATABASE_URI="sqlite:///blog.sqlite3",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    # If someone passed in test config (like during testing), use that instead.
    if test_config:
        app.config.update(test_config)

    # Make sure the instance folder exists so SQLite has somewhere to live.
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    db.init_app(app)
    login_manager.init_app(app)

    # Import blueprints here to dodge circular import issues.
    from . import models
    from .auth import auth_bp
    from .main import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    # This lets every template know how many unread notifications the logged-in
    # user has, so we can show a little badge in the nav.
    @app.context_processor
    def inject_unread_notifications():
        from flask_login import current_user

        unread_count = 0
        if current_user.is_authenticated:
            unread_count = models.Notification.query.filter_by(
                user_id=current_user.id, is_read=False
            ).count()
        return {"unread_notifications": unread_count}

    # Create all tables on startup. In production you'd probably use migrations,
    # but this keeps things simple for a small blog.
    with app.app_context():
        db.create_all()

    return app


@login_manager.user_loader
def load_user(user_id):
    from .models import User

    # Flask-Login calls this to reload a user from their ID stored in the session.
    return db.session.get(User, int(user_id))

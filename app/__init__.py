from pathlib import Path

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy


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

    if test_config:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    db.init_app(app)
    login_manager.init_app(app)

    from . import models
    from .auth import auth_bp
    from .main import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    @app.context_processor
    def inject_unread_notifications():
        from flask_login import current_user

        unread_count = 0
        if current_user.is_authenticated:
            unread_count = models.Notification.query.filter_by(
                user_id=current_user.id, is_read=False
            ).count()
        return {"unread_notifications": unread_count}

    with app.app_context():
        db.create_all()

    return app


@login_manager.user_loader
def load_user(user_id):
    from .models import User

    return db.session.get(User, int(user_id))

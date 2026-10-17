from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from . import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    posts = db.relationship("Post", backref="author", lazy=True, cascade="all, delete-orphan")
    comments = db.relationship("Comment", backref="author", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    comments = db.relationship("Comment", backref="post", lazy=True, cascade="all, delete-orphan")
    likes = db.relationship("Like", backref="post", lazy=True, cascade="all, delete-orphan")


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    __table_args__ = (db.UniqueConstraint("user_id", "post_id", name="unique_user_post_like"),)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    actor_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    kind = db.Column(db.String(20), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

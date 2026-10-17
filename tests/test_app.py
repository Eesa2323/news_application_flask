import pytest

from app import create_app, db
from app.models import Notification, Post, User


@pytest.fixture
def client(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-key",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'test.sqlite3'}",
        }
    )
    with app.test_client() as client:
        yield client
    with app.app_context():
        db.drop_all()


def signup(client, username, email):
    return client.post(
        "/auth/signup",
        data={"username": username, "email": email, "password": "password"},
        follow_redirects=True,
    )


def login(client, identifier):
    return client.post(
        "/auth/login",
        data={"identifier": identifier, "password": "password"},
        follow_redirects=True,
    )


def test_blog_crud_and_notifications(client):
    signup(client, "writer", "writer@example.com")
    response = client.post(
        "/post/new",
        data={"title": "First note", "body": "A thought worth sharing."},
        follow_redirects=True,
    )
    assert b"First note" in response.data

    with client.application.app_context():
        post = Post.query.one()
        post_id = post.id

    client.post("/auth/logout")
    signup(client, "reader", "reader@example.com")
    client.post(f"/post/{post_id}/like", follow_redirects=True)
    client.post(f"/post/{post_id}/comment", data={"body": "This stayed with me."})

    with client.application.app_context():
        assert Notification.query.count() == 2

    client.post("/auth/logout")
    login(client, "writer")
    inbox = client.get("/notifications")
    assert b"reader liked your post" in inbox.data
    assert b"reader commented on your post" in inbox.data

    edited = client.post(
        f"/post/{post_id}/edit",
        data={"title": "Updated note", "body": "Updated body."},
        follow_redirects=True,
    )
    assert b"Updated note" in edited.data

    deleted = client.post(f"/post/{post_id}/delete", follow_redirects=True)
    assert b"Post deleted" in deleted.data
    with client.application.app_context():
        assert Post.query.count() == 0

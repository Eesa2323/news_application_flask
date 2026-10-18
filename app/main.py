from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import desc

from . import db
from .models import Comment, Like, Notification, Post


main_bp = Blueprint("main", __name__)


def notify(post, kind, message):
    # Only ping the post author if someone else is doing the liking/commenting.
    # No point notifying you about your own activity.
    if post.user_id != current_user.id:
        db.session.add(Notification(user_id=post.user_id, actor_id=current_user.id, post_id=post.id, kind=kind, message=message))


@main_bp.route("/")
def index():
    # Grab every post, newest first, for the home page feed.
    posts = Post.query.order_by(desc(Post.created_at)).all()
    return render_template("index.html", posts=posts)


@main_bp.route("/post/new", methods=["GET", "POST"])
@login_required
def create_post():
    if request.method == "POST":
        title = request.form["title"].strip()
        body = request.form["body"].strip()
        if not title or not body:
            flash("A title and body are required.", "error")
        else:
            post = Post(title=title, body=body, author=current_user)
            db.session.add(post)
            db.session.commit()
            flash("Your story is live.", "success")
            return redirect(url_for("main.post_detail", post_id=post.id))
    return render_template("post_form.html", post=None)


@main_bp.route("/post/<int:post_id>")
def post_detail(post_id):
    post = db.get_or_404(Post, post_id)
    # Figure out if the current user already liked this post so we can show
    # the right button state (filled heart vs outline).
    liked = current_user.is_authenticated and Like.query.filter_by(user_id=current_user.id, post_id=post.id).first()
    return render_template("post_detail.html", post=post, liked=liked)


@main_bp.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    post = db.get_or_404(Post, post_id)
    if post.user_id != current_user.id:
        flash("You can only edit your own posts.", "error")
        return redirect(url_for("main.post_detail", post_id=post.id))
    if request.method == "POST":
        post.title = request.form["title"].strip()
        post.body = request.form["body"].strip()
        if not post.title or not post.body:
            flash("A title and body are required.", "error")
        else:
            db.session.commit()
            flash("Post updated.", "success")
            return redirect(url_for("main.post_detail", post_id=post.id))
    return render_template("post_form.html", post=post)


@main_bp.post("/post/<int:post_id>/delete")
@login_required
def delete_post(post_id):
    post = db.get_or_404(Post, post_id)
    if post.user_id != current_user.id:
        flash("You can only delete your own posts.", "error")
    else:
        db.session.delete(post)
        db.session.commit()
        flash("Post deleted.", "success")
    return redirect(url_for("main.index"))


@main_bp.post("/post/<int:post_id>/like")
@login_required
def toggle_like(post_id):
    post = db.get_or_404(Post, post_id)
    like = Like.query.filter_by(user_id=current_user.id, post_id=post.id).first()
    if like:
        # They already liked it, so unlike it.
        db.session.delete(like)
    else:
        db.session.add(Like(user_id=current_user.id, post_id=post.id))
        notify(post, "like", f"{current_user.username} liked your post.")
    db.session.commit()
    return redirect(request.referrer or url_for("main.post_detail", post_id=post.id))


@main_bp.post("/post/<int:post_id>/comment")
@login_required
def add_comment(post_id):
    post = db.get_or_404(Post, post_id)
    body = request.form["body"].strip()
    if body:
        db.session.add(Comment(body=body, user_id=current_user.id, post_id=post.id))
        notify(post, "comment", f"{current_user.username} commented on your post.")
        db.session.commit()
    return redirect(url_for("main.post_detail", post_id=post.id))


@main_bp.route("/notifications")
@login_required
def notifications():
    items = Notification.query.filter_by(user_id=current_user.id).order_by(desc(Notification.created_at)).all()
    for item in items:
        item.is_read = True
    db.session.commit()
    return render_template("notifications.html", notifications=items)

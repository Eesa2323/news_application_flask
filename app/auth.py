from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import or_

from . import db
from .models import User


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    if request.method == "POST":
        username = request.form["username"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        if not username or not email or len(password) < 6:
            flash("Use a username, email, and a password of at least 6 characters.", "error")
        elif User.query.filter(or_(User.username == username, User.email == email)).first():
            flash("That username or email is already in use.", "error")
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash("Welcome to Ink & Signal.", "success")
            return redirect(url_for("main.index"))
    return render_template("auth/signup.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    if request.method == "POST":
        identifier = request.form["identifier"].strip()
        user = User.query.filter(or_(User.username == identifier, User.email == identifier.lower())).first()
        if not user or not user.check_password(request.form["password"]):
            flash("Those credentials did not match.", "error")
        else:
            login_user(user)
            return redirect(request.args.get("next") or url_for("main.index"))
    return render_template("auth/login.html")


@auth_bp.post("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("main.index"))

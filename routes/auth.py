from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from extensions import db
from models import User
from forms import RegistrationForm, LoginForm, ProfileForm

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = User(
                username=form.username.data.strip(),
                email=form.email.data.strip().lower(),
                password_hash=generate_password_hash(form.password.data.strip()),
            )
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash("Registration successful. Welcome!", "success")
            return redirect(url_for("dashboard.index"))
        except IntegrityError:
            db.session.rollback()
            flash("Username or Email already exists.", "danger")
    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user and check_password_hash(user.password_hash, form.password.data.strip()):
            login_user(user, remember=form.remember.data)
            flash("Logged in successfully.", "success")
            next_url = request.args.get("next")
            return redirect(next_url or url_for("dashboard.index"))
        flash("Invalid credentials.", "danger")
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.username = form.username.data.strip()
        current_user.email = form.email.data.strip().lower()
        current_user.calorie_goal = form.calorie_goal.data
        current_user.water_goal_ml = form.water_goal_ml.data
        current_user.dark_mode = bool(form.dark_mode.data)
        try:
            db.session.commit()
            flash("Profile updated.", "success")
            return redirect(url_for("auth.profile"))
        except IntegrityError:
            db.session.rollback()
            flash("Username or Email already exists.", "danger")
    return render_template("auth/profile.html", form=form)
from datetime import date, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy import func
from extensions import db
from models import WaterIntake, Sleep
from forms import WaterForm, SleepForm

extras_bp = Blueprint("extras", __name__, url_prefix="/extras")


@extras_bp.route("/water", methods=["GET", "POST"])
@login_required
def water():
    form = WaterForm()
    today = date.today()
    if form.validate_on_submit():
        entry = WaterIntake(user_id=current_user.id, date=form.date.data, amount_ml=form.amount_ml.data)
        db.session.add(entry)
        db.session.commit()
        flash("Water intake logged.", "success")
        return redirect(url_for("extras.water"))

    # Today progress
    total_today = db.session.query(func.sum(WaterIntake.amount_ml)).filter_by(
        user_id=current_user.id, date=today
    ).scalar() or 0
    pct = int(min(100, (total_today / max(1, current_user.water_goal_ml)) * 100))

    return render_template("extras/water.html", form=form, total_today=total_today, pct=pct)


@extras_bp.route("/water/quick", methods=["POST"])
@login_required
def water_quick():
    amt = int(request.form.get("amount", 250))
    entry = WaterIntake(user_id=current_user.id, date=date.today(), amount_ml=amt)
    db.session.add(entry)
    db.session.commit()
    flash(f"Added {amt}ml water.", "success")
    return redirect(url_for("extras.water"))


@extras_bp.route("/sleep", methods=["GET", "POST"])
@login_required
def sleep():
    form = SleepForm()
    if form.validate_on_submit():
        entry = Sleep(
            user_id=current_user.id,
            date=form.date.data,
            hours_slept=form.hours_slept.data,
            quality_rating=int(form.quality_rating.data) if form.quality_rating.data else None,
        )
        db.session.add(entry)
        db.session.commit()
        flash("Sleep log added.", "success")
        return redirect(url_for("extras.sleep"))

    # Stats for last 7 days
    today = date.today()
    start = today - timedelta(days=6)
    logs = Sleep.query.filter(
        Sleep.user_id == current_user.id,
        Sleep.date >= start,
        Sleep.date <= today,
    ).order_by(Sleep.date.desc()).all()

    avg_hours = round(sum(l.hours_slept for l in logs) / len(logs), 1) if logs else 0.0

    return render_template("extras/sleep.html", form=form, logs=logs, avg_hours=avg_hours)


@extras_bp.route("/exercises/library", methods=["GET"])
@login_required
def exercise_library():
    # Simple built-in library; could be extended to DB-backed
    library = [
        {"name": "Squat", "category": "Strength", "description": "Compound lower-body movement.", "tips": "Keep chest up, drive knees out."},
        {"name": "Bench Press", "category": "Strength", "description": "Chest press with barbell.", "tips": "Feet planted, control the bar."},
        {"name": "Deadlift", "category": "Strength", "description": "Hip hinge pulling movement.", "tips": "Neutral spine, engage lats."},
        {"name": "Running", "category": "Cardio", "description": "Steady-state or intervals.", "tips": "Warm up and pace appropriately."},
        {"name": "Yoga Sun Salutation", "category": "Yoga", "description": "Flow to warm up body.", "tips": "Focus on breath and alignment."},
    ]
    return render_template("exercises/library.html", library=library)
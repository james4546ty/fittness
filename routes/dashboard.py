from datetime import date, timedelta
from collections import Counter, defaultdict
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from sqlalchemy import func
from extensions import db
from models import Workout, Nutrition, BodyMetrics, WaterIntake, Sleep

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("/", methods=["GET"])
@login_required
def index():
    # Recent workouts
    recent_workouts = Workout.query.filter_by(user_id=current_user.id).order_by(Workout.date.desc()).limit(5).all()

    # Weekly activity summary (last 7 days)
    today = date.today()
    start_week = today - timedelta(days=6)
    week_workouts = Workout.query.filter(
        Workout.user_id == current_user.id,
        Workout.date >= start_week,
        Workout.date <= today,
    ).all()
    day_counts = Counter([w.date.isoformat() for w in week_workouts])

    # Calories intake vs goal (today)
    total_cal_today = db.session.query(func.sum(Nutrition.calories)).filter_by(user_id=current_user.id, date=today).scalar() or 0
    remaining_cal_today = max(0, (current_user.calorie_goal or 0) - total_cal_today)

    # Weight progress chart (last 30 days)
    start_month = today - timedelta(days=30)
    weight_points = BodyMetrics.query.filter(
        BodyMetrics.user_id == current_user.id,
        BodyMetrics.date >= start_month,
        BodyMetrics.date <= today,
    ).order_by(BodyMetrics.date.asc()).all()

    # Workout frequency heatmap (last 30 days)
    recent_workouts_month = Workout.query.filter(
        Workout.user_id == current_user.id,
        Workout.date >= start_month,
        Workout.date <= today,
    ).all()
    freq_by_day = Counter([w.date.isoformat() for w in recent_workouts_month])

    # Statistics
    total_workouts = Workout.query.filter_by(user_id=current_user.id).count()
    total_time = db.session.query(func.sum(Workout.duration)).filter_by(user_id=current_user.id).scalar() or 0
    avg_calories_burned = db.session.query(func.avg(Workout.calories_burned)).filter(
        Workout.user_id == current_user.id,
        Workout.calories_burned.isnot(None),
    ).scalar() or 0

    return render_template(
        "dashboard/index.html",
        recent_workouts=recent_workouts,
        day_counts=day_counts,
        total_cal_today=total_cal_today,
        remaining_cal_today=remaining_cal_today,
        weight_points=weight_points,
        freq_by_day=freq_by_day,
        stats={"total_workouts": total_workouts, "total_time": total_time, "avg_calories_burned": int(avg_calories_burned)},
    )


@dashboard_bp.route("/report", methods=["GET"])
@login_required
def report():
    range_ = request.args.get("range", "week")
    today = date.today()
    if range_ == "month":
        start = today - timedelta(days=30)
    else:
        start = today - timedelta(days=7)

    workouts = Workout.query.filter(
        Workout.user_id == current_user.id,
        Workout.date >= start,
        Workout.date <= today,
    ).order_by(Workout.date.desc()).all()

    nutrition = Nutrition.query.filter(
        Nutrition.user_id == current_user.id,
        Nutrition.date >= start,
        Nutrition.date <= today,
    ).order_by(Nutrition.date.desc()).all()

    metrics = BodyMetrics.query.filter(
        BodyMetrics.user_id == current_user.id,
        BodyMetrics.date >= start,
        BodyMetrics.date <= today,
    ).order_by(BodyMetrics.date.desc()).all()

    # Totals
    total_time = sum(w.duration for w in workouts)
    total_workouts = len(workouts)
    total_calories_food = sum(n.calories for n in nutrition)
    avg_weight = round(sum(m.weight for m in metrics) / len(metrics), 1) if metrics else None

    return render_template(
        "dashboard/report.html",
        range_=range_,
        total_time=total_time,
        total_workouts=total_workouts,
        total_calories_food=total_calories_food,
        avg_weight=avg_weight,
        workouts=workouts,
        nutrition=nutrition,
        metrics=metrics,
    )
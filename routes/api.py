from datetime import date, timedelta
from collections import defaultdict, Counter
from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import Workout, Nutrition, BodyMetrics

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/dashboard-data", methods=["GET"])
@login_required
def dashboard_data():
    today = date.today()
    start_month = today - timedelta(days=30)
    start_week = today - timedelta(days=6)

    # Weight points
    weights = BodyMetrics.query.filter(
        BodyMetrics.user_id == current_user.id,
        BodyMetrics.date >= start_month,
        BodyMetrics.date <= today,
    ).order_by(BodyMetrics.date.asc()).all()
    weight_series = [{"x": m.date.isoformat(), "y": m.weight} for m in weights]

    # Calories intake vs goal (last 7 days)
    calories_daily = []
    for i in range(7):
        d = today - timedelta(days=(6 - i))
        total = sum(n.calories for n in Nutrition.query.filter_by(user_id=current_user.id, date=d).all())
        calories_daily.append({"date": d.isoformat(), "calories": total, "goal": current_user.calorie_goal})

    # Workout frequency heatmap (last 30 days)
    workouts = Workout.query.filter(
        Workout.user_id == current_user.id,
        Workout.date >= start_month,
        Workout.date <= today,
    ).all()
    freq = Counter([w.date.isoformat() for w in workouts])
    heatmap = [{"date": d, "count": c} for d, c in freq.items()]

    return jsonify({
        "weight_series": weight_series,
        "calories_daily": calories_daily,
        "heatmap": heatmap,
    })
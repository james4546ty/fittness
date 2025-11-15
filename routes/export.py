import csv
import io
from datetime import date
from flask import Blueprint, Response, render_template
from flask_login import login_required, current_user
from models import Workout, Exercise, Nutrition, BodyMetrics, Goal, WaterIntake, Sleep

export_bp = Blueprint("export", __name__, url_prefix="/export")


@export_bp.route("/", methods=["GET"])
@login_required
def index():
    return render_template("export/index.html")


def as_csv(rows, headers, filename):
    proxy = io.StringIO()
    writer = csv.writer(proxy)
    writer.writerow(headers)
    for r in rows:
        writer.writerow(r)
    mem = io.BytesIO()
    mem.write(proxy.getvalue().encode("utf-8"))
    mem.seek(0)
    proxy.close()
    return Response(
        mem,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@export_bp.route("/workouts.csv", methods=["GET"])
@login_required
def export_workouts():
    ws = Workout.query.filter_by(user_id=current_user.id).order_by(Workout.date.asc()).all()
    rows = []
    for w in ws:
        rows.append([w.id, w.date.isoformat(), w.type, w.duration, w.calories_burned or 0, (w.notes or "").replace("\\n", " ")])
        for e in w.exercises:
            rows.append([f"exercise:{e.id}", "", e.name, e.sets or "", e.reps or "", e.weight or ""])
    return as_csv(rows, ["id", "date", "type/name", "duration/sets", "calories/reps", "notes/weight"], "workouts.csv")


@export_bp.route("/nutrition.csv", methods=["GET"])
@login_required
def export_nutrition():
    ns = Nutrition.query.filter_by(user_id=current_user.id).order_by(Nutrition.date.asc()).all()
    rows = [[n.id, n.date.isoformat(), n.meal_type, n.food_name, n.calories, n.protein, n.carbs, n.fats] for n in ns]
    return as_csv(rows, ["id", "date", "meal_type", "food", "calories", "protein", "carbs", "fats"], "nutrition.csv")


@export_bp.route("/metrics.csv", methods=["GET"])
@login_required
def export_metrics():
    ms = BodyMetrics.query.filter_by(user_id=current_user.id).order_by(BodyMetrics.date.asc()).all()
    rows = [[m.id, m.date.isoformat(), m.weight, m.body_fat_percentage or "", m.measurements or "", m.photo_path or ""] for m in ms]
    return as_csv(rows, ["id", "date", "weight", "body_fat_%", "measurements_json", "photo_path"], "metrics.csv")


@export_bp.route("/goals.csv", methods=["GET"])
@login_required
def export_goals():
    gs = Goal.query.filter_by(user_id=current_user.id).order_by(Goal.deadline.asc().nulls_last()).all()
    rows = [[g.id, g.goal_type, g.target_value, g.current_value or "", g.deadline.isoformat() if g.deadline else "", g.status] for g in gs]
    return as_csv(rows, ["id", "goal_type", "target_value", "current_value", "deadline", "status"], "goals.csv")


@export_bp.route("/lifestyle.csv", methods=["GET"])
@login_required
def export_lifestyle():
    ws = WaterIntake.query.filter_by(user_id=current_user.id).order_by(WaterIntake.date.asc()).all()
    ss = Sleep.query.filter_by(user_id=current_user.id).order_by(Sleep.date.asc()).all()
    rows = [["water", w.date.isoformat(), w.amount_ml, "", ""] for w in ws]
    rows += [["sleep", s.date.isoformat(), s.hours_slept, s.quality_rating or "", ""] for s in ss]
    return as_csv(rows, ["type", "date", "amount/hours", "quality", ""], "lifestyle.csv")
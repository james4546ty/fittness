from datetime import date, timedelta
from collections import defaultdict
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy import func
from extensions import db
from models import Nutrition, User
from forms import NutritionForm, FilterForm

nutrition_bp = Blueprint("nutrition", __name__, url_prefix="/nutrition")


def paginate_query(query, page, per_page=10):
    items = query.limit(per_page).offset((page - 1) * per_page).all()
    total = query.order_by(None).count()
    return {
        "items": items,
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": (total + per_page - 1) // per_page,
    }


@nutrition_bp.route("/", methods=["GET"])
@login_required
def list_nutrition():
    form = FilterForm(request.args)
    page = int(request.args.get("page", 1))
    q = Nutrition.query.filter_by(user_id=current_user.id)

    if form.start_date.data:
        q = q.filter(Nutrition.date >= form.start_date.data)
    if form.end_date.data:
        q = q.filter(Nutrition.date <= form.end_date.data)
    if form.meal_type.data:
        q = q.filter(Nutrition.meal_type == form.meal_type.data)

    q = q.order_by(Nutrition.date.desc(), Nutrition.id.desc())
    pagination = paginate_query(q, page, per_page=12)

    # Daily remaining calories
    today = date.today()
    total_cal = db.session.query(func.sum(Nutrition.calories)).filter_by(user_id=current_user.id, date=today).scalar() or 0
    remaining = max(0, (current_user.calorie_goal or 0) - total_cal)

    return render_template("nutrition/list.html", nutrition=pagination, form=form, remaining=remaining)


@nutrition_bp.route("/new", methods=["GET", "POST"])
@login_required
def new_nutrition():
    form = NutritionForm()
    if form.validate_on_submit():
        entry = Nutrition(
            user_id=current_user.id,
            date=form.date.data,
            meal_type=form.meal_type.data,
            food_name=form.food_name.data.strip(),
            calories=form.calories.data,
            protein=form.protein.data,
            carbs=form.carbs.data,
            fats=form.fats.data,
        )
        db.session.add(entry)
        db.session.commit()
        flash("Nutrition entry added.", "success")
        return redirect(url_for("nutrition.list_nutrition"))
    return render_template("nutrition/form.html", form=form, title="Add Nutrition")


@nutrition_bp.route("/<int:item_id>/edit", methods=["GET", "POST"])
@login_required
def edit_nutrition(item_id: int):
    entry = Nutrition.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    form = NutritionForm(obj=entry)
    if form.validate_on_submit():
        entry.date = form.date.data
        entry.meal_type = form.meal_type.data
        entry.food_name = form.food_name.data.strip()
        entry.calories = form.calories.data
        entry.protein = form.protein.data
        entry.carbs = form.carbs.data
        entry.fats = form.fats.data
        db.session.commit()
        flash("Nutrition entry updated.", "success")
        return redirect(url_for("nutrition.list_nutrition"))
    return render_template("nutrition/form.html", form=form, title="Edit Nutrition")


@nutrition_bp.route("/<int:item_id>/delete", methods=["POST"])
@login_required
def delete_nutrition(item_id: int):
    entry = Nutrition.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    db.session.delete(entry)
    db.session.commit()
    flash("Entry deleted.", "info")
    return redirect(url_for("nutrition.list_nutrition"))


@nutrition_bp.route("/summary", methods=["GET"])
@login_required
def summary():
    range_ = request.args.get("range", "week")
    today = date.today()
    if range_ == "day":
        start = today
    elif range_ == "month":
        start = today - timedelta(days=30)
    else:
        start = today - timedelta(days=7)

    q = Nutrition.query.filter(
        Nutrition.user_id == current_user.id,
        Nutrition.date >= start,
        Nutrition.date <= today,
    )

    # Aggregate by day
    daily = defaultdict(lambda: {"calories": 0, "protein": 0.0, "carbs": 0.0, "fats": 0.0})
    for n in q.all():
        key = n.date.isoformat()
        daily[key]["calories"] += n.calories
        daily[key]["protein"] += n.protein
        daily[key]["carbs"] += n.carbs
        daily[key]["fats"] += n.fats

    # Totals
    totals = {"calories": 0, "protein": 0.0, "carbs": 0.0, "fats": 0.0}
    for d in daily.values():
        for k in totals:
            totals[k] += d[k]

    return render_template("nutrition/summary.html", daily=daily, totals=totals, range_=range_)
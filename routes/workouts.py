from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from sqlalchemy import and_
from extensions import db
from models import Workout, Exercise
from forms import WorkoutForm, ExerciseForm, FilterForm

workouts_bp = Blueprint("workouts", __name__, url_prefix="/workouts")


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


@workouts_bp.route("/", methods=["GET"])
@login_required
def list_workouts():
    form = FilterForm(request.args)
    page = int(request.args.get("page", 1))
    q = Workout.query.filter_by(user_id=current_user.id)

    # Filtering
    if form.start_date.data:
        q = q.filter(Workout.date >= form.start_date.data)
    if form.end_date.data:
        q = q.filter(Workout.date <= form.end_date.data)
    if form.type.data:
        q = q.filter(Workout.type == form.type.data)

    q = q.order_by(Workout.date.desc(), Workout.id.desc())

    pagination = paginate_query(q, page, per_page=10)
    return render_template("workouts/list.html", workouts=pagination, form=form)


@workouts_bp.route("/new", methods=["GET", "POST"])
@login_required
def new_workout():
    form = WorkoutForm()
    if form.validate_on_submit():
        workout = Workout(
            user_id=current_user.id,
            date=form.date.data,
            type=form.type.data,
            duration=form.duration.data,
            calories_burned=form.calories_burned.data,
            notes=form.notes.data,
        )
        db.session.add(workout)
        db.session.commit()
        flash("Workout logged.", "success")
        return redirect(url_for("workouts.view_workout", workout_id=workout.id))
    return render_template("workouts/form.html", form=form, title="Log Workout")


@workouts_bp.route("/<int:workout_id>", methods=["GET"])
@login_required
def view_workout(workout_id: int):
    workout = Workout.query.filter_by(id=workout_id, user_id=current_user.id).first_or_404()
    ex_form = ExerciseForm()
    return render_template("workouts/detail.html", workout=workout, ex_form=ex_form)


@workouts_bp.route("/<int:workout_id>/edit", methods=["GET", "POST"])
@login_required
def edit_workout(workout_id: int):
    workout = Workout.query.filter_by(id=workout_id, user_id=current_user.id).first_or_404()
    form = WorkoutForm(obj=workout)
    if form.validate_on_submit():
        workout.date = form.date.data
        workout.type = form.type.data
        workout.duration = form.duration.data
        workout.calories_burned = form.calories_burned.data
        workout.notes = form.notes.data
        db.session.commit()
        flash("Workout updated.", "success")
        return redirect(url_for("workouts.view_workout", workout_id=workout.id))
    return render_template("workouts/form.html", form=form, title="Edit Workout")


@workouts_bp.route("/<int:workout_id>/delete", methods=["POST"])
@login_required
def delete_workout(workout_id: int):
    workout = Workout.query.filter_by(id=workout_id, user_id=current_user.id).first_or_404()
    db.session.delete(workout)
    db.session.commit()
    flash("Workout deleted.", "info")
    return redirect(url_for("workouts.list_workouts"))


@workouts_bp.route("/<int:workout_id>/exercise/add", methods=["POST"])
@login_required
def add_exercise(workout_id: int):
    workout = Workout.query.filter_by(id=workout_id, user_id=current_user.id).first_or_404()
    form = ExerciseForm()
    if form.validate_on_submit():
        ex = Exercise(
            workout_id=workout.id,
            name=form.name.data.strip(),
            sets=form.sets.data,
            reps=form.reps.data,
            weight=form.weight.data,
        )
        db.session.add(ex)
        db.session.commit()
        flash("Exercise added.", "success")
    else:
        flash("Invalid exercise details.", "danger")
    return redirect(url_for("workouts.view_workout", workout_id=workout.id))


@workouts_bp.route("/exercise/<int:exercise_id>/delete", methods=["POST"])
@login_required
def delete_exercise(exercise_id: int):
    ex = Exercise.query.get_or_404(exercise_id)
    workout = ex.workout
    if workout.user_id != current_user.id:
        abort(403)
    db.session.delete(ex)
    db.session.commit()
    flash("Exercise removed.", "info")
    return redirect(url_for("workouts.view_workout", workout_id=workout.id))
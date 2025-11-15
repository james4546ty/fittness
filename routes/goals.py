from datetime import date
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models import Goal
from forms import GoalForm

goals_bp = Blueprint("goals", __name__, url_prefix="/goals")


@goals_bp.route("/", methods=["GET"])
@login_required
def list_goals():
    goals = Goal.query.filter_by(user_id=current_user.id).order_by(Goal.deadline.asc().nulls_last()).all()
    return render_template("goals/list.html", goals=goals, form=GoalForm())


@goals_bp.route("/new", methods=["GET", "POST"])
@login_required
def new_goal():
    form = GoalForm()
    if form.validate_on_submit():
        goal = Goal(
            user_id=current_user.id,
            goal_type=form.goal_type.data,
            target_value=form.target_value.data,
            current_value=form.current_value.data,
            deadline=form.deadline.data,
            status=form.status.data,
        )
        db.session.add(goal)
        db.session.commit()
        flash("Goal created.", "success")
        return redirect(url_for("goals.list_goals"))
    return render_template("goals/form.html", form=form, title="New Goal")


@goals_bp.route("/<int:goal_id>/edit", methods=["GET", "POST"])
@login_required
def edit_goal(goal_id: int):
    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
    form = GoalForm(obj=goal)
    if form.validate_on_submit():
        prev_progress = goal.progress_percent()
        goal.goal_type = form.goal_type.data
        goal.target_value = form.target_value.data
        goal.current_value = form.current_value.data
        goal.deadline = form.deadline.data
        goal.status = form.status.data
        db.session.commit()

        # Milestone notifications
        now_progress = goal.progress_percent()
        if prev_progress < 50 <= now_progress:
            flash("Milestone reached: 50% progress!", "info")
        if prev_progress < 100 <= now_progress:
            flash("Milestone reached: 100% goal achieved!", "success")

        flash("Goal updated.", "success")
        return redirect(url_for("goals.list_goals"))
    return render_template("goals/form.html", form=form, title="Edit Goal")


@goals_bp.route("/<int:goal_id>/delete", methods=["POST"])
@login_required
def delete_goal(goal_id: int):
    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
    db.session.delete(goal)
    db.session.commit()
    flash("Goal deleted.", "info")
    return redirect(url_for("goals.list_goals"))
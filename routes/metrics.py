import os
import uuid
import json
from datetime import date
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from models import BodyMetrics
from forms import BodyMetricsForm

metrics_bp = Blueprint("metrics", __name__, url_prefix="/metrics")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@metrics_bp.route("/", methods=["GET"])
@login_required
def list_metrics():
    q = BodyMetrics.query.filter_by(user_id=current_user.id).order_by(BodyMetrics.date.desc(), BodyMetrics.id.desc())
    metrics = q.all()
    return render_template("metrics/list.html", metrics=metrics)


@metrics_bp.route("/new", methods=["GET", "POST"])
@login_required
def new_metrics():
    form = BodyMetricsForm()
    if form.validate_on_submit():
        measurements = {
            "height_cm": form.height_cm.data,
            "chest": form.chest.data,
            "waist": form.waist.data,
            "hips": form.hips.data,
            "arms": form.arms.data,
            "legs": form.legs.data,
        }

        photo_path = None
        if form.photo.data and allowed_file(form.photo.data.filename):
            filename = secure_filename(form.photo.data.filename)
            ext = filename.rsplit(".", 1)[1].lower()
            unique = f"{uuid.uuid4().hex}.{ext}"
            dest = os.path.join(current_app.config["UPLOAD_FOLDER"], unique)
            form.photo.data.save(dest)
            photo_path = unique

        bm = BodyMetrics(
            user_id=current_user.id,
            date=form.date.data,
            weight=form.weight.data,
            body_fat_percentage=form.body_fat_percentage.data,
            measurements=json.dumps({k: v for k, v in measurements.items() if v is not None}),
            photo_path=photo_path,
        )
        db.session.add(bm)
        db.session.commit()
        flash("Body metrics saved.", "success")
        return redirect(url_for("metrics.list_metrics"))
    return render_template("metrics/form.html", form=form, title="Add Metrics")


@metrics_bp.route("/<int:metrics_id>/edit", methods=["GET", "POST"])
@login_required
def edit_metrics(metrics_id: int):
    bm = BodyMetrics.query.filter_by(id=metrics_id, user_id=current_user.id).first_or_404()
    mdata = bm.measurements_dict()
    form = BodyMetricsForm(
        date=bm.date,
        weight=bm.weight,
        body_fat_percentage=bm.body_fat_percentage,
        height_cm=mdata.get("height_cm"),
        chest=mdata.get("chest"),
        waist=mdata.get("waist"),
        hips=mdata.get("hips"),
        arms=mdata.get("arms"),
        legs=mdata.get("legs"),
    )
    if form.validate_on_submit():
        measurements = {
            "height_cm": form.height_cm.data,
            "chest": form.chest.data,
            "waist": form.waist.data,
            "hips": form.hips.data,
            "arms": form.arms.data,
            "legs": form.legs.data,
        }

        photo_path = bm.photo_path
        if form.photo.data and allowed_file(form.photo.data.filename):
            filename = secure_filename(form.photo.data.filename)
            ext = filename.rsplit(".", 1)[1].lower()
            unique = f"{uuid.uuid4().hex}.{ext}"
            dest = os.path.join(current_app.config["UPLOAD_FOLDER"], unique)
            form.photo.data.save(dest)
            photo_path = unique

        bm.date = form.date.data
        bm.weight = form.weight.data
        bm.body_fat_percentage = form.body_fat_percentage.data
        bm.measurements = json.dumps({k: v for k, v in measurements.items() if v is not None})
        bm.photo_path = photo_path
        db.session.commit()
        flash("Body metrics updated.", "success")
        return redirect(url_for("metrics.list_metrics"))
    return render_template("metrics/form.html", form=form, title="Edit Metrics")
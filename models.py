from datetime import datetime, date
import json
from typing import Optional
from flask_login import UserMixin
from sqlalchemy import CheckConstraint
from extensions import db, login_manager


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Preferences / goals
    calorie_goal = db.Column(db.Integer, default=2000, nullable=False)
    water_goal_ml = db.Column(db.Integer, default=2000, nullable=False)
    dark_mode = db.Column(db.Boolean, default=False, nullable=False)

    workouts = db.relationship("Workout", backref="user", lazy=True, cascade="all, delete-orphan")
    nutrition_logs = db.relationship("Nutrition", backref="user", lazy=True, cascade="all, delete-orphan")
    metrics = db.relationship("BodyMetrics", backref="user", lazy=True, cascade="all, delete-orphan")
    goals = db.relationship("Goal", backref="user", lazy=True, cascade="all, delete-orphan")
    water = db.relationship("WaterIntake", backref="user", lazy=True, cascade="all, delete-orphan")
    sleep = db.relationship("Sleep", backref="user", lazy=True, cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User {self.username}>"


@login_manager.user_loader
def load_user(user_id: str) -> Optional["User"]:
    return User.query.get(int(user_id))


class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    date = db.Column(db.Date, default=date.today, nullable=False, index=True)
    type = db.Column(db.String(50), nullable=False, index=True)
    duration = db.Column(db.Integer, nullable=False)  # minutes
    calories_burned = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    exercises = db.relationship("Exercise", backref="workout", lazy=True, cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Workout {self.type} {self.date}>"


class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey("workout.id"), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    sets = db.Column(db.Integer, nullable=True)
    reps = db.Column(db.Integer, nullable=True)
    weight = db.Column(db.Float, nullable=True)  # kg

    def __repr__(self) -> str:
        return f"<Exercise {self.name}>"


class Nutrition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    date = db.Column(db.Date, default=date.today, nullable=False, index=True)
    meal_type = db.Column(db.String(20), nullable=False, index=True)  # breakfast, lunch, dinner, snack
    food_name = db.Column(db.String(120), nullable=False)
    calories = db.Column(db.Integer, nullable=False)
    protein = db.Column(db.Float, nullable=False)  # grams
    carbs = db.Column(db.Float, nullable=False)    # grams
    fats = db.Column(db.Float, nullable=False)     # grams

    def __repr__(self) -> str:
        return f"<Nutrition {self.meal_type} {self.date}>"


class BodyMetrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    date = db.Column(db.Date, default=date.today, nullable=False, index=True)
    weight = db.Column(db.Float, nullable=False)  # kg
    body_fat_percentage = db.Column(db.Float, nullable=True)

    # Measurements stored as JSON string: {"chest":..., "waist":..., ...}
    measurements = db.Column(db.Text, nullable=True)
    photo_path = db.Column(db.String(255), nullable=True)

    __table_args__ = (
        CheckConstraint("weight >= 0", name="ck_metrics_weight_nonnegative"),
    )

    def measurements_dict(self):
        try:
            return json.loads(self.measurements) if self.measurements else {}
        except Exception:
            return {}

    @property
    def bmi(self) -> Optional[float]:
        m = self.measurements_dict()
        height_cm = m.get("height_cm")
        if height_cm and height_cm > 0:
            height_m = float(height_cm) / 100.0
            return round(float(self.weight) / (height_m ** 2), 2)
        return None

    def __repr__(self) -> str:
        return f"<BodyMetrics {self.date} wt={self.weight}>"


class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    goal_type = db.Column(db.String(50), nullable=False)  # weight_loss, strength, endurance, etc.
    target_value = db.Column(db.Float, nullable=False)
    current_value = db.Column(db.Float, nullable=True)
    deadline = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(30), default="active", nullable=False)

    def progress_percent(self) -> float:
        if self.current_value is None or self.target_value == 0:
            return 0.0
        pct = (self.current_value / self.target_value) * 100.0
        return max(0.0, min(100.0, pct))

    def __repr__(self) -> str:
        return f"<Goal {self.goal_type} {self.progress_percent():.1f}%>"


class WaterIntake(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    date = db.Column(db.Date, default=date.today, nullable=False, index=True)
    amount_ml = db.Column(db.Integer, nullable=False)

    def __repr__(self) -> str:
        return f"<Water {self.date} {self.amount_ml}ml>"


class Sleep(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    date = db.Column(db.Date, default=date.today, nullable=False, index=True)
    hours_slept = db.Column(db.Float, nullable=False)
    quality_rating = db.Column(db.Integer, nullable=True)  # 1-5

    def __repr__(self) -> str:
        return f"<Sleep {self.date} {self.hours_slept}h>"
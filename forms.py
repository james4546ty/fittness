from datetime import date
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    IntegerField,
    FloatField,
    TextAreaField,
    DateField,
    SelectField,
    FileField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    EqualTo,
    NumberRange,
    Optional,
    ValidationError,
)

WORKOUT_TYPES = ["cardio", "strength", "yoga", "sports", "mobility", "other"]
MEAL_TYPES = ["breakfast", "lunch", "dinner", "snack"]


def validate_password_complexity(form, field):
    pwd = field.data or ""
    if (len(pwd) < 8
        or not any(c.islower() for c in pwd)
        or not any(c.isupper() for c in pwd)
        or not any(c.isdigit() for c in pwd)
    ):
        raise ValidationError("Password must be at least 8 characters with upper, lower, and numeric characters.")


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired(), validate_password_complexity])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")


class ProfileForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    calorie_goal = IntegerField("Daily Calorie Goal", validators=[DataRequired(), NumberRange(min=500, max=10000)])
    water_goal_ml = IntegerField("Daily Water Goal (ml)", validators=[DataRequired(), NumberRange(min=250, max=10000)])
    dark_mode = BooleanField("Dark Mode")
    submit = SubmitField("Save")


class WorkoutForm(FlaskForm):
    date = DateField("Date", validators=[DataRequired()], default=date.today)
    type = SelectField("Type", validators=[DataRequired()], choices=[(t, t.title()) for t in WORKOUT_TYPES])
    duration = IntegerField("Duration (min)", validators=[DataRequired(), NumberRange(min=1, max=1440)])
    calories_burned = IntegerField("Calories Burned", validators=[Optional(), NumberRange(min=0, max=10000)])
    notes = TextAreaField("Notes", validators=[Optional(), Length(max=2000)])
    submit = SubmitField("Save")


class ExerciseForm(FlaskForm):
    name = StringField("Exercise Name", validators=[DataRequired(), Length(max=100)])
    sets = IntegerField("Sets", validators=[Optional(), NumberRange(min=0, max=100)])
    reps = IntegerField("Reps", validators=[Optional(), NumberRange(min=0, max=1000)])
    weight = FloatField("Weight (kg)", validators=[Optional(), NumberRange(min=0, max=1000)])
    submit = SubmitField("Add Exercise")


class NutritionForm(FlaskForm):
    date = DateField("Date", validators=[DataRequired()], default=date.today)
    meal_type = SelectField("Meal Type", validators=[DataRequired()], choices=[(m, m.title()) for m in MEAL_TYPES])
    food_name = StringField("Food Name", validators=[DataRequired(), Length(max=120)])
    calories = IntegerField("Calories", validators=[DataRequired(), NumberRange(min=0, max=5000)])
    protein = FloatField("Protein (g)", validators=[DataRequired(), NumberRange(min=0, max=500)])
    carbs = FloatField("Carbs (g)", validators=[DataRequired(), NumberRange(min=0, max=1000)])
    fats = FloatField("Fats (g)", validators=[DataRequired(), NumberRange(min=0, max=500)])
    submit = SubmitField("Save")


class BodyMetricsForm(FlaskForm):
    date = DateField("Date", validators=[DataRequired()], default=date.today)
    weight = FloatField("Weight (kg)", validators=[DataRequired(), NumberRange(min=0, max=500)])
    body_fat_percentage = FloatField("Body Fat (%)", validators=[Optional(), NumberRange(min=0, max=100)])
    height_cm = FloatField("Height (cm)", validators=[Optional(), NumberRange(min=30, max=300)])
    chest = FloatField("Chest (cm)", validators=[Optional(), NumberRange(min=0, max=300)])
    waist = FloatField("Waist (cm)", validators=[Optional(), NumberRange(min=0, max=300)])
    hips = FloatField("Hips (cm)", validators=[Optional(), NumberRange(min=0, max=300)])
    arms = FloatField("Arms (cm)", validators=[Optional(), NumberRange(min=0, max=300)])
    legs = FloatField("Legs (cm)", validators=[Optional(), NumberRange(min=0, max=300)])
    photo = FileField("Progress Photo", validators=[Optional()])
    submit = SubmitField("Save")


class GoalForm(FlaskForm):
    goal_type = SelectField("Goal Type", validators=[DataRequired()],
                            choices=[("weight_loss", "Weight Loss"),
                                     ("weight_gain", "Weight Gain"),
                                     ("strength", "Strength"),
                                     ("endurance", "Endurance"),
                                     ("other", "Other")])
    target_value = FloatField("Target Value", validators=[DataRequired(), NumberRange(min=0)])
    current_value = FloatField("Current Value", validators=[Optional(), NumberRange(min=0)])
    deadline = DateField("Deadline", validators=[Optional()])
    status = SelectField("Status", validators=[DataRequired()], choices=[("active", "Active"), ("paused", "Paused"), ("completed", "Completed")])
    submit = SubmitField("Save")


class WaterForm(FlaskForm):
    date = DateField("Date", validators=[DataRequired()], default=date.today)
    amount_ml = IntegerField("Amount (ml)", validators=[DataRequired(), NumberRange(min=10, max=10000)])
    submit = SubmitField("Add")


class SleepForm(FlaskForm):
    date = DateField("Date", validators=[DataRequired()], default=date.today)
    hours_slept = FloatField("Hours Slept", validators=[DataRequired(), NumberRange(min=0, max=24)])
    quality_rating = SelectField("Quality Rating", validators=[Optional()], choices=[(str(i), str(i)) for i in range(1, 6)])
    submit = SubmitField("Add")


class FilterForm(FlaskForm):
    start_date = DateField("Start Date", validators=[Optional()])
    end_date = DateField("End Date", validators=[Optional()])
    type = SelectField("Type", validators=[Optional()], choices=[("", "All")] + [(t, t.title()) for t in WORKOUT_TYPES])
    meal_type = SelectField("Meal Type", validators=[Optional()], choices=[("", "All")] + [(m, m.title()) for m in MEAL_TYPES])
    submit = SubmitField("Filter")
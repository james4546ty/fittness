# Fitness Tracker Flask App

A complete fitness tracker web application built with Flask, SQLite, Flask-Login, Flask-WTF, Bootstrap 5, and Chart.js.

## Features

- User authentication (register, login, logout), password hashing
- User profile with editable preferences (calorie goals, water goal, dark mode)
- Workout tracking with exercises, edit/delete, filters, pagination
- Nutrition tracking with macros, daily remaining calories, summaries
- Body metrics tracking (weight, measurements, body fat, optional progress photos)
- Goals and progress with progress percentages and milestone notifications
- Dashboard & analytics (recent workouts, weekly activity, calorie vs goal, weight chart, frequency heatmap, statistics)
- Water intake tracker with daily goal and quick-add
- Sleep tracking with quality rating
- Exercise library
- Export data to CSV
- Mobile-responsive design with Bootstrap 5
- CSRF protection, input validation, XSS-safe templates

## Project Structure

- app.py — application factory and bootstrap
- models.py — SQLAlchemy models
- forms.py — Flask-WTF forms and validators
- routes/ — blueprints (auth, workouts, nutrition, metrics, goals, dashboard, extras, export, api)
- templates/ — Jinja2 templates with template inheritance
- static/ — CSS, JS, and uploads (progress photos)
- tests/ — basic unit tests
- requirements.txt — dependencies

## Getting Started

1) Create and activate a virtual environment

```
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
```

2) Install dependencies

```
pip install -r requirements.txt
```

3) Run the app

```
export FLASK_APP=app:app
export FLASK_ENV=development
python main.py
# or: flask run
```

Then open http://127.0.0.1:5000/dashboard/ in your browser.

Optional environment variables:

- SECRET_KEY — Flask session secret (default is a development key)
- DATABASE_URL — SQLAlchemy database URI (default: sqlite:///fitness_tracker.db)
- SESSION_COOKIE_SECURE — set to 1 when serving over HTTPS

Progress photos are stored in static/uploads.

## Testing

Run tests with:

```
pytest -q
```

## Security Notes

- Passwords are hashed using Werkzeug
- All forms include CSRF tokens (Flask-WTF)
- ORM with parameterized queries guards against SQL injection
- Jinja auto-escaping mitigates XSS
- Session cookies are HttpOnly, SameSite=Lax; enable Secure in production

## License

MIT

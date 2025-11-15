import pytest
from app import create_app
from extensions import db
from werkzeug.security import generate_password_hash
from models import User, Workout

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
    })
    with app.app_context():
        db.create_all()
        yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_user(app):
    with app.app_context():
        user = User(username="wuser", email="wuser@example.com", password_hash=generate_password_hash("StrongPass123"))
        db.session.add(user)
        db.session.commit()
        return user

def login(client, user):
    return client.post("/auth/login", data={"email": user.email, "password": "StrongPass123"}, follow_redirects=True)

def test_add_workout(client, app, auth_user):
    # login
    login(client, auth_user)

    # create workout
    resp = client.post("/workouts/new", data={
        "date": "2025-01-01",
        "type": "cardio",
        "duration": 30,
        "calories_burned": 250,
        "notes": "Test run"
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Workout logged." in resp.data

    with app.app_context():
        assert Workout.query.filter_by(user_id=auth_user.id).count() == 1
import pytest
from app import create_app
from extensions import db
from models import User
from werkzeug.security import generate_password_hash

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

def test_register_and_login(client, app):
    # Register
    resp = client.post("/auth/register", data={
        "username": "tester",
        "email": "tester@example.com",
        "password": "StrongPass123",
        "confirm_password": "StrongPass123",
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Registration successful" in resp.data

    # Logout
    client.get("/auth/logout", follow_redirects=True)

    # Login
    resp = client.post("/auth/login", data={
        "email": "tester@example.com",
        "password": "StrongPass123",
        "remember": "y",
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Logged in successfully" in resp.data

def test_profile_update(client, app):
    # Create user
    with app.app_context():
        u = User(username="u1", email="u1@example.com", password_hash=generate_password_hash("pw12345A"))
        db.session.add(u)
        db.session.commit()

    # Login
    client.post("/auth/login", data={"email": "u1@example.com", "password": "pw12345A"}, follow_redirects=True)

    # Profile (should require proper password normally; here we're testing form plumbing)
    resp = client.post("/auth/profile", data={
        "username": "u1new",
        "email": "u1@example.com",
        "calorie_goal": 2200,
        "water_goal_ml": 2500,
        "dark_mode": "y",
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Profile updated" in resp.data
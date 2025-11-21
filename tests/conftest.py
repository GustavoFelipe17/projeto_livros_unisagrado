# tests/conftest.py
import pytest
from app import create_app
from app.models import db

@pytest.fixture(scope='module')
def test_app():
    config_overrides = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "LOGIN_DISABLED": True
    }

    app = create_app(config_overrides)

    with app.app_context():
        db.create_all()

        yield app

        db.drop_all()

@pytest.fixture(scope='module')
def test_client(test_app):
    return test_app.test_client()
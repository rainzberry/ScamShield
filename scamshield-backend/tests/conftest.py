import pytest

from app import create_app
from app.config import TestConfig
from tests.fake_engine import FakeEngine

PASSWORD = "Str0ngPassw0rd"


@pytest.fixture()
def engine():
    return FakeEngine()


@pytest.fixture()
def app(engine):
    return create_app(TestConfig, ml_engine=engine)


@pytest.fixture()
def client(app):
    return app.test_client()


def register(client, email="alice@example.com", password=PASSWORD):
    res = client.post("/api/auth/register", json={"email": email, "password": password})
    assert res.status_code == 201, res.get_json()
    return {"Authorization": f"Bearer {res.get_json()['access_token']}"}


@pytest.fixture()
def auth(client):
    return register(client)


@pytest.fixture()
def auth_b(client):
    return register(client, "bob@example.com")

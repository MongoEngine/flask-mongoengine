import pytest
from flask import session

from flask_mongoengine import MongoEngineSessionInterface


@pytest.fixture(autouse=True)
def setup_endpoints(app, db):

    app.session_interface = MongoEngineSessionInterface(db)

    @app.route("/")
    def index():
        session["a"] = "hello session"
        return session["a"]

    @app.route("/check-session")
    def check_session():
        return "session: %s" % session["a"]

    @app.route("/check-session-database")
    def check_session_database():
        sessions = app.session_interface.cls.objects.count()
        return "sessions: %s" % sessions


def test_setting_session(app):
    client = app.test_client()

    response = client.get("/")
    assert response.status_code == 200
    assert response.data.decode("utf-8") == "hello session"

    response = client.get("/check-session")
    assert response.status_code == 200
    assert response.data.decode("utf-8") == "session: hello session"

    response = client.get("/check-session-database")
    assert response.status_code == 200
    assert response.data.decode("utf-8") == "sessions: 1"

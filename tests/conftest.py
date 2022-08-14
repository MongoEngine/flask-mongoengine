from datetime import datetime
from typing import NoReturn

import mongoengine
import pytest
from flask import Flask
from pymongo import MongoClient

from flask_mongoengine import MongoEngine


@pytest.fixture(autouse=True, scope="session")
def session_clean_up() -> NoReturn:
    """Mandatory tests environment clean up before/after test session."""
    client = MongoClient("localhost", 27017)
    client.drop_database("flask_mongoengine_test_db")
    client.drop_database("flask_mongoengine_test_db_1")
    client.drop_database("flask_mongoengine_test_db_2")

    yield

    client.drop_database("flask_mongoengine_test_db")
    client.drop_database("flask_mongoengine_test_db_1")
    client.drop_database("flask_mongoengine_test_db_2")


@pytest.fixture()
def app() -> Flask:
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        yield app

    mongoengine.connection.disconnect_all()


@pytest.fixture()
def db(app) -> MongoEngine:
    app.config["MONGODB_SETTINGS"] = [
        {
            "db": "flask_mongoengine_test_db",
            "host": "localhost",
            "port": 27017,
            "alias": "default",
            "uuidRepresentation": "standard",
        }
    ]
    test_db = MongoEngine(app)
    db_name = (
        test_db.connection["default"].get_database("flask_mongoengine_test_db").name
    )

    if not db_name.endswith("_test_db"):
        raise RuntimeError(
            f"DATABASE_URL must point to testing db, not to master db ({db_name})"
        )

    # Clear database before tests, for cases when some test failed before.
    test_db.connection["default"].drop_database(db_name)

    yield test_db

    # Clear database after tests, for graceful exit.
    test_db.connection["default"].drop_database(db_name)


@pytest.fixture()
def todo(db):
    class Todo(db.Document):
        title = mongoengine.StringField(max_length=60)
        text = mongoengine.StringField()
        done = mongoengine.BooleanField(default=False)
        pub_date = mongoengine.DateTimeField(default=datetime.utcnow)
        comments = mongoengine.ListField(mongoengine.StringField())
        comment_count = mongoengine.IntField()

    return Todo

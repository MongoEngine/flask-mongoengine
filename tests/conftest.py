from datetime import datetime

import mongoengine
import pytest
from flask import Flask

from flask_mongoengine import MongoEngine


@pytest.fixture()
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        yield app

    mongoengine.connection.disconnect_all()


@pytest.fixture()
def db(app):
    app.config["MONGODB_HOST"] = "mongodb://localhost:27017/flask_mongoengine_test_db"
    test_db = MongoEngine(app)
    db_name = test_db.connection.get_database("flask_mongoengine_test_db").name

    if not db_name.endswith("_test_db"):
        raise RuntimeError(
            f"DATABASE_URL must point to testing db, not to master db ({db_name})"
        )

    # Clear database before tests, for cases when some test failed before.
    test_db.connection.drop_database(db_name)

    yield test_db

    # Clear database after tests, for graceful exit.
    test_db.connection.drop_database(db_name)


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

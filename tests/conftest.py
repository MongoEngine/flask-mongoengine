import mongoengine
import pytest
from flask import Flask


@pytest.fixture()
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True

    with app.app_context():
        yield app

    mongoengine.connection.disconnect_all()


@pytest.fixture()
def todo(db):
    class Todo(db.Document):
        # meta = {"db_alias": alias}
        title = mongoengine.StringField(max_length=60)
        text = mongoengine.StringField()
        done = mongoengine.BooleanField(default=False)

    return Todo

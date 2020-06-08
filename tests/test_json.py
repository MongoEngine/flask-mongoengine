import flask
import pytest

from flask_mongoengine import MongoEngine


@pytest.fixture()
def extended_db(app):
    app.json_encoder = DummyEncoder
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


class DummyEncoder(flask.json.JSONEncoder):
    """
    An example encoder which a user may create and override
    the apps json_encoder with.
    This class is a NO-OP, but used to test proper inheritance.
    """


@pytest.mark.usefixtures("extended_db")
def test_inheritance(app):
    assert issubclass(app.json_encoder, DummyEncoder)
    json_encoder_name = app.json_encoder.__name__

    # Since the class is dynamically derrived, must compare class names
    # rather than class objects.
    assert json_encoder_name == "MongoEngineJSONEncoder"

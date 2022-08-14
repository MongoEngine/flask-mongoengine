"""Extension of app JSON capabilities."""
import flask
import pytest

from flask_mongoengine import MongoEngine
from flask_mongoengine.json import use_json_provider


@pytest.fixture()
def extended_db(app):
    """Provider config fixture."""
    if use_json_provider():
        app.json_provider_class = DummyProvider
    else:
        app.json_encoder = DummyEncoder
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


class DummyEncoder(flask.json.JSONEncoder):
    """
    An example encoder which a user may create and override
    the apps json_encoder with.
    This class is a NO-OP, but used to test proper inheritance.
    """


DummyProvider = None
if use_json_provider():

    class DummyProvider(flask.json.provider.DefaultJSONProvider):
        """Dummy Provider, to test correct MRO in new flask versions."""


@pytest.mark.skipif(condition=use_json_provider(), reason="New flask use other test")
@pytest.mark.usefixtures("extended_db")
def test_inheritance_old_flask(app):
    assert issubclass(app.json_encoder, DummyEncoder)
    json_encoder_name = app.json_encoder.__name__

    assert json_encoder_name == "MongoEngineJSONEncoder"


@pytest.mark.skipif(
    condition=not use_json_provider(), reason="Old flask use other test"
)
@pytest.mark.usefixtures("extended_db")
def test_inheritance(app):
    assert issubclass(app.json_provider_class, DummyProvider)
    json_provider_class = app.json_provider_class.__name__

    assert json_provider_class == "MongoEngineJSONProvider"
    assert isinstance(app.json, DummyProvider)

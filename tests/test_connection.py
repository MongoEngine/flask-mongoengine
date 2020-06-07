import mongoengine
import pytest
from mongoengine.connection import ConnectionFailure
from pymongo.database import Database
from pymongo.mongo_client import MongoClient
from pymongo.errors import InvalidURI
from flask_mongoengine import MongoEngine, current_mongoengine_instance


def test_connection__should_use_defaults__if_no_settings_provided(app):
    """Make sure a simple connection to a standalone MongoDB works."""
    db = MongoEngine()

    # Verify no extension for Mongoengine yet created for app
    assert app.extensions == {}
    assert current_mongoengine_instance() is None

    # Create db connection. Should return None.
    assert db.init_app(app) is None

    # Verify db added to Flask extensions.
    assert current_mongoengine_instance() == db

    # Verify db settings passed to pymongo driver.
    # Default mongoengine db is 'default', default Flask-Mongoengine db is 'test'.
    connection = mongoengine.get_connection()
    mongo_engine_db = mongoengine.get_db()
    assert isinstance(mongo_engine_db, Database)
    assert isinstance(connection, MongoClient)
    assert mongo_engine_db.name == "test"
    assert connection.HOST == "localhost"
    assert connection.PORT == 27017


@pytest.mark.parametrize(
    ("config_extension"),
    [
        {
            "MONGODB_SETTINGS": {
                "ALIAS": "simple_conn",
                "HOST": "localhost",
                "PORT": 27017,
                "DB": "flask_mongoengine_test_db",
            }
        },
        {
            "MONGODB_HOST": "localhost",
            "MONGODB_PORT": 27017,
            "MONGODB_DB": "flask_mongoengine_test_db",
            "MONGODB_ALIAS": "simple_conn",
        },
    ],
    ids=("Dict format", "Config variable format"),
)
def test_connection__should_pass_alias__if_provided(app, config_extension):
    """Make sure a simple connection pass ALIAS setting variable."""
    db = MongoEngine()
    app.config.update(config_extension)

    # Verify no extension for Mongoengine yet created for app
    assert app.extensions == {}
    assert current_mongoengine_instance() is None

    # Create db connection. Should return None.
    assert db.init_app(app) is None

    # Verify db added to Flask extensions.
    assert current_mongoengine_instance() == db

    # Verify db settings passed to pymongo driver.
    # ALIAS is used to find correct connection.
    # As we do not use default alias, default call to mongoengine.get_connection
    # should raise.
    with pytest.raises(ConnectionFailure):
        mongoengine.get_connection()

    connection = mongoengine.get_connection("simple_conn")
    mongo_engine_db = mongoengine.get_db("simple_conn")
    assert isinstance(mongo_engine_db, Database)
    assert isinstance(connection, MongoClient)
    assert mongo_engine_db.name == "flask_mongoengine_test_db"
    assert connection.HOST == "localhost"
    assert connection.PORT == 27017


@pytest.mark.parametrize(
    ("config_extension"),
    [
        {
            "MONGODB_SETTINGS": {
                "HOST": "mongodb://localhost:27017/flask_mongoengine_test_db"
            }
        },
        {
            "MONGODB_HOST": "mongodb://localhost:27017/flask_mongoengine_test_db",
            "MONGODB_PORT": 27017,
            "MONGODB_DB": "should_ignore_it",
        },
    ],
    ids=("Dict format", "Config variable format"),
)
def test_connection__should_parse_host_uri__if_host_formatted_as_uri(
    app, config_extension
):
    """Make sure a simple connection pass ALIAS setting variable."""
    db = MongoEngine()
    app.config.update(config_extension)

    # Verify no extension for Mongoengine yet created for app
    assert app.extensions == {}
    assert current_mongoengine_instance() is None

    # Create db connection. Should return None.
    assert db.init_app(app) is None

    # Verify db added to Flask extensions.
    assert current_mongoengine_instance() == db

    connection = mongoengine.get_connection()
    mongo_engine_db = mongoengine.get_db()
    assert isinstance(mongo_engine_db, Database)
    assert isinstance(connection, MongoClient)
    assert mongo_engine_db.name == "flask_mongoengine_test_db"
    assert connection.HOST == "localhost"
    assert connection.PORT == 27017


@pytest.mark.parametrize(
    ("config_extension"),
    [
        {
            "MONGODB_SETTINGS": {
                "HOST": "mongomock://localhost:27017/flask_mongoengine_test_db"
            }
        },
        {
            "MONGODB_SETTINGS": {
                "ALIAS": "simple_conn",
                "HOST": "localhost",
                "PORT": 27017,
                "DB": "flask_mongoengine_test_db",
                "IS_MOCK": True,
            }
        },
        {"MONGODB_HOST": "mongomock://localhost:27017/flask_mongoengine_test_db"},
    ],
    ids=("Dict format as URI", "Dict format as Param", "Config variable format as URI"),
)
def test_connection__should_parse_mongo_mock_uri__as_uri_and_as_settings(
    app, config_extension
):
    """Make sure a simple connection pass ALIAS setting variable."""
    db = MongoEngine()
    app.config.update(config_extension)

    # Verify no extension for Mongoengine yet created for app
    assert app.extensions == {}
    assert current_mongoengine_instance() is None

    # Create db connection. Should return None.

    with pytest.raises(RuntimeError) as error:
        assert db.init_app(app) is None

    assert str(error.value) == "You need mongomock installed to mock MongoEngine."


@pytest.mark.parametrize(
    ("config_extension"),
    [
        {
            "MONGODB_SETTINGS": {
                "HOST": "postgre://localhost:27017/flask_mongoengine_test_db"
            }
        },
        {"MONGODB_HOST": "mysql://localhost:27017/flask_mongoengine_test_db"},
    ],
    ids=("Dict format as URI", "Config variable format as URI"),
)
def test_connection__should_raise__if_uri_not_properly_formatted(app, config_extension):
    """Make sure a simple connection pass ALIAS setting variable."""
    db = MongoEngine()
    app.config.update(config_extension)

    # Verify no extension for Mongoengine yet created for app
    assert app.extensions == {}
    assert current_mongoengine_instance() is None

    # Create db connection. Should return None.

    with pytest.raises(InvalidURI) as error:
        assert db.init_app(app) is None

    assert (
        str(error.value)
        == "Invalid URI scheme: URI must begin with 'mongodb://' or 'mongodb+srv://'"
    )

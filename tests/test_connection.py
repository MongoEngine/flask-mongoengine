import mongoengine
import pymongo
import pytest
from mongoengine.connection import ConnectionFailure
from mongoengine.context_managers import switch_db
from pymongo.database import Database
from pymongo.errors import InvalidURI
from pymongo.mongo_client import MongoClient
from pymongo.read_preferences import ReadPreference

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


def test_connection__should_accept_host_as_list(app):
    """Make sure MONGODB_HOST can be a list hosts."""
    db = MongoEngine()
    app.config["MONGODB_SETTINGS"] = {
        "ALIAS": "host_list",
        "HOST": ["localhost:27017"],
        "DB": "flask_mongoengine_list_test_db",
    }
    db.init_app(app)

    connection = mongoengine.get_connection("host_list")
    mongo_engine_db = mongoengine.get_db("host_list")
    assert isinstance(mongo_engine_db, Database)
    assert isinstance(connection, MongoClient)
    assert mongo_engine_db.name == "flask_mongoengine_list_test_db"
    assert connection.HOST == "localhost"
    assert connection.PORT == 27017


def test_multiple_connections(app):
    """Make sure establishing multiple connections to a standalone
    MongoDB and switching between them works.
    """
    db = MongoEngine()
    app.config["MONGODB_SETTINGS"] = [
        {
            "ALIAS": "default",
            "DB": "flask_mongoengine_test_db_1",
            "HOST": "localhost",
            "PORT": 27017,
        },
        {
            "ALIAS": "alternative",
            "DB": "flask_mongoengine_test_db_2",
            "HOST": "localhost",
            "PORT": 27017,
        },
    ]

    class Todo(db.Document):
        title = db.StringField(max_length=60)

    db.init_app(app)
    # Drop default collection from init
    Todo.drop_collection()
    Todo.meta = {"db_alias": "alternative"}
    # Drop 'alternative' collection initiated early.
    Todo.drop_collection()

    # Make sure init correct and both databases are clean
    with switch_db(Todo, "default") as Todo:
        doc = Todo.objects().first()
        assert doc is None

    with switch_db(Todo, "alternative") as Todo:
        doc = Todo.objects().first()
        assert doc is None

    # Test saving a doc via the default connection
    with switch_db(Todo, "default") as Todo:
        todo = Todo()
        todo.text = "Sample"
        todo.title = "Testing"
        todo.done = True
        s_todo = todo.save()

        f_to = Todo.objects().first()
        assert s_todo.title == f_to.title

    # Make sure the doc still doesn't exist in the alternative db
    with switch_db(Todo, "alternative") as Todo:
        doc = Todo.objects().first()
        assert doc is None

    # Make sure switching back to the default connection shows the doc
    with switch_db(Todo, "default") as Todo:
        doc = Todo.objects().first()
        assert doc is not None


def test_ingnored_mongodb_prefix_config(app):
    """Config starting by MONGODB_ but not used by flask-mongoengine
    should be ignored.
    """
    db = MongoEngine()
    app.config[
        "MONGODB_HOST"
    ] = "mongodb://localhost:27017/flask_mongoengine_test_db_prod"
    # Invalid host, should trigger exception if used
    app.config["MONGODB_TEST_HOST"] = "dummy://localhost:27017/test"
    db.init_app(app)

    connection = mongoengine.get_connection()
    mongo_engine_db = mongoengine.get_db()
    assert isinstance(mongo_engine_db, Database)
    assert isinstance(connection, MongoClient)
    assert mongo_engine_db.name == "flask_mongoengine_test_db_prod"
    assert connection.HOST == "localhost"
    assert connection.PORT == 27017


def test_connection_kwargs(app):
    """Make sure additional connection kwargs work."""

    # Figure out whether to use "MAX_POOL_SIZE" or "MAXPOOLSIZE" based
    # on PyMongo version (former was changed to the latter as described
    # in https://jira.mongodb.org/browse/PYTHON-854)
    # TODO remove once PyMongo < 3.0 support is dropped
    if pymongo.version_tuple[0] >= 3:
        MAX_POOL_SIZE_KEY = "MAXPOOLSIZE"
    else:
        MAX_POOL_SIZE_KEY = "MAX_POOL_SIZE"

    app.config["MONGODB_SETTINGS"] = {
        "ALIAS": "tz_aware_true",
        "DB": "flask_mongoengine_testing_tz_aware",
        "TZ_AWARE": True,
        "READ_PREFERENCE": ReadPreference.SECONDARY,
        MAX_POOL_SIZE_KEY: 10,
    }
    db = MongoEngine(app)

    assert db.connection.codec_options.tz_aware
    assert db.connection.max_pool_size == 10
    assert db.connection.read_preference == ReadPreference.SECONDARY

"""
Tests for ``MongoDebugPanel`` and related mongo events listener.

- Independent of global configuration by design.
"""
import contextlib

import jinja2
import pymongo
import pytest
from flask import Flask

flask_debugtoolbar = pytest.importorskip("flask_debugtoolbar")

from flask_debugtoolbar import DebugToolbarExtension  # noqa
from flask_debugtoolbar.panels import DebugPanel  # noqa
from jinja2 import ChoiceLoader, DictLoader  # noqa
from pymongo import monitoring  # noqa
from pymongo.errors import OperationFailure  # noqa
from pytest_mock import MockerFixture  # noqa

from flask_mongoengine.panels import (  # noqa
    MongoCommandLogger,
    MongoDebugPanel,
    _maybe_patch_jinja_loader,
    mongo_command_logger,
)


@pytest.fixture()
def app_no_mongo_monitoring() -> Flask:
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["SECRET_KEY"] = "flask+mongoengine=<3"
    app.debug = True
    app.config["DEBUG_TB_PANELS"] = ("flask_mongoengine.panels.MongoDebugPanel",)
    app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
    DebugToolbarExtension(app)
    with app.app_context():
        yield app


@pytest.fixture(autouse=True)
def registered_monitoring() -> MongoCommandLogger:
    """Register/Unregister mongo_command_logger in required tests"""
    monitoring.register(mongo_command_logger)
    mongo_command_logger.reset_tracker()
    yield mongo_command_logger
    # Unregister listener between independent tests
    mongo_command_logger.reset_tracker()
    with contextlib.suppress(ValueError):
        monitoring._LISTENERS.command_listeners.remove(mongo_command_logger)


def test__maybe_patch_jinja_loader__replace_loader_when_initial_loader_is_not_choice_loader():
    jinja2_env = jinja2.Environment()
    assert not isinstance(jinja2_env.loader, ChoiceLoader)
    _maybe_patch_jinja_loader(jinja2_env)
    assert isinstance(jinja2_env.loader, ChoiceLoader)


def test__maybe_patch_jinja_loader__extend_loader_when_initial_loader_is_choice_loader():
    jinja2_env = jinja2.Environment(loader=ChoiceLoader([DictLoader({"1": "1"})]))
    assert isinstance(jinja2_env.loader, ChoiceLoader)
    assert len(jinja2_env.loader.loaders) == 1
    _maybe_patch_jinja_loader(jinja2_env)
    assert len(jinja2_env.loader.loaders) == 2


class TestMongoDebugPanel:
    """Trivial tests to highlight any unexpected changes in namings or code."""

    @pytest.fixture
    def toolbar_with_no_flask(self) -> MongoDebugPanel:
        """Simple instance of MongoDebugPanel without flask application"""
        jinja2_env = jinja2.Environment()
        return MongoDebugPanel(jinja2_env)

    def test__panel_name_and_static_properties_not_modified(
        self, toolbar_with_no_flask
    ):
        assert toolbar_with_no_flask.name == "MongoDB"
        assert toolbar_with_no_flask.title() == "MongoDB Operations"
        assert toolbar_with_no_flask.nav_title() == "MongoDB"
        assert toolbar_with_no_flask.url() == ""

    def test__config_error_message_not_modified(self, toolbar_with_no_flask):
        assert toolbar_with_no_flask.config_error_message == (
            "Pymongo monitoring configuration error. mongo_command_logger should be "
            "registered before database connection."
        )

    def test__is_properly_configured__return_false__when_mongo_command_logger__not_registered(
        self, toolbar_with_no_flask, caplog
    ):
        """Also verify logging done."""
        # Emulate not working state(against auto used registered_monitoring fixture)
        mongo_command_logger.reset_tracker()
        monitoring._LISTENERS.command_listeners.remove(mongo_command_logger)
        assert toolbar_with_no_flask.is_properly_configured is False
        assert caplog.messages[0] == toolbar_with_no_flask.config_error_message

    def test__is_properly_configured__return_true__when_mongo_command_logger_registered(
        self,
        toolbar_with_no_flask,
    ):
        assert toolbar_with_no_flask.is_properly_configured is True

    def test__nav_subtitle__return_config_error_message__when_toolbar_incorrectly_configured(
        self, toolbar_with_no_flask
    ):
        """Also check that content flag changed."""
        # Emulate not working state(against auto used registered_monitoring fixture)
        mongo_command_logger.reset_tracker()
        monitoring._LISTENERS.command_listeners.remove(mongo_command_logger)
        # First line is before nav_subtitle() call
        assert toolbar_with_no_flask.has_content is True

        assert (
            toolbar_with_no_flask.nav_subtitle()
            == toolbar_with_no_flask.config_error_message
        )
        assert toolbar_with_no_flask.has_content is False

    def test__nav_subtitle__return_correct_message_when_toolbar_correctly_configured(
        self,
        toolbar_with_no_flask,
    ):
        assert toolbar_with_no_flask.nav_subtitle() == "0 operations, in  0.00ms"
        assert toolbar_with_no_flask.has_content is True

    def test__context__is_empty_by_default(self, app, toolbar_with_no_flask):
        assert toolbar_with_no_flask._context == {
            "queries": [],
            "slow_query_limit": 100,
        }

    def test__process_request__correctly_resets_monitoring__without_instance_replace(
        self,
        registered_monitoring,
        app,
        toolbar_with_no_flask,
    ):
        # sourcery skip: simplify-empty-collection-comparison
        # Test setup
        initial_id = id(registered_monitoring)
        # Inject some fakes to monitoring engine
        registered_monitoring.total_time = 1
        registered_monitoring.started_operations_count = 1
        registered_monitoring.succeeded_operations_count = 1
        registered_monitoring.failed_operations_count = 1
        registered_monitoring.queries = [1, 2]
        registered_monitoring.started_events = {1: 1, 2: 2}

        # Pre-test validation
        assert registered_monitoring.total_time == 1
        assert registered_monitoring.started_operations_count == 1
        assert registered_monitoring.succeeded_operations_count == 1
        assert registered_monitoring.failed_operations_count == 1
        assert registered_monitoring.queries == [1, 2]
        assert registered_monitoring.started_events == {1: 1, 2: 2}
        toolbar_with_no_flask.process_request(None)

        assert id(registered_monitoring) == initial_id
        assert registered_monitoring.total_time == 0
        assert registered_monitoring.started_operations_count == 0
        assert registered_monitoring.succeeded_operations_count == 0
        assert registered_monitoring.failed_operations_count == 0
        assert registered_monitoring.queries == []
        assert registered_monitoring.started_events == {}

    def test__content__calls_parent__render__function(
        self,
        app,
        toolbar_with_no_flask,
        mocker: MockerFixture,
    ):
        spy = mocker.patch.object(DebugPanel, "render", autospec=True)
        toolbar_with_no_flask.content()
        spy.assert_called_with(
            toolbar_with_no_flask,
            "panels/mongo-panel.html",
            toolbar_with_no_flask._context,
        )


class TestMongoCommandLogger:
    """By design tested with raw pymongo."""

    @pytest.fixture(autouse=True)
    def py_db(self, registered_monitoring) -> pymongo.MongoClient:
        """Clean up and returns special database for testing on pymongo driver level"""
        client = pymongo.MongoClient("localhost", 27017)
        db = client.pymongo_test_database
        client.drop_database(db)
        registered_monitoring.reset_tracker()
        yield db
        client.drop_database(db)

    def test__normal_command__logged(self, py_db, registered_monitoring):
        post = {
            "author": "Mike",
            "text": "My first blog post!",
            "tags": ["mongodb", "python", "pymongo"],
        }

        py_db.posts.insert_one(post)
        assert registered_monitoring.started_operations_count == 1
        assert registered_monitoring.succeeded_operations_count == 1
        assert registered_monitoring.queries[0].time >= 0
        assert registered_monitoring.queries[0].size >= 0
        assert registered_monitoring.queries[0].database == "pymongo_test_database"
        assert registered_monitoring.queries[0].collection == "posts"
        assert registered_monitoring.queries[0].command_name == "insert"
        assert isinstance(registered_monitoring.queries[0].operation_id, int)
        assert len(registered_monitoring.queries[0].server_command["documents"]) == 1
        assert registered_monitoring.queries[0].server_response == {"n": 1, "ok": 1.0}
        assert registered_monitoring.queries[0].request_status == "Succeed"

    def test__failed_command_logged__logged(self, py_db, registered_monitoring):
        """Failed command index 1 in provided test."""
        pymongo.collection.Collection(py_db, "test", create=True)
        with contextlib.suppress(OperationFailure):
            pymongo.collection.Collection(py_db, "test", create=True)
        assert registered_monitoring.started_operations_count == 2
        assert registered_monitoring.succeeded_operations_count == 1
        assert registered_monitoring.failed_operations_count == 1
        assert registered_monitoring.queries[0].time >= 0
        assert registered_monitoring.queries[0].size >= 0
        assert registered_monitoring.queries[0].database == "pymongo_test_database"
        assert registered_monitoring.queries[0].collection == "test"
        assert registered_monitoring.queries[0].command_name == "create"
        assert isinstance(registered_monitoring.queries[0].operation_id, int)
        assert registered_monitoring.queries[0].server_command["create"] == "test"
        assert registered_monitoring.queries[0].server_response == {"ok": 1.0}
        assert registered_monitoring.queries[0].request_status == "Succeed"
        assert registered_monitoring.queries[1].time >= 0
        assert registered_monitoring.queries[1].size >= 0
        assert registered_monitoring.queries[1].database == "pymongo_test_database"
        assert registered_monitoring.queries[1].collection == "test"
        assert registered_monitoring.queries[1].command_name == "create"
        assert isinstance(registered_monitoring.queries[1].operation_id, int)
        assert registered_monitoring.queries[1].server_command["create"] == "test"
        assert (
            "already exists"
            in registered_monitoring.queries[1].server_response["errmsg"]
        )
        assert registered_monitoring.queries[1].request_status == "Failed"

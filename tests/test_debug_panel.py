"""
Tests for ``MongoDebugPanel`` and related mongo events listener.

- Independent of global configuration by design.
"""
import jinja2
import pytest
from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from flask_debugtoolbar.panels import DebugPanel
from jinja2 import ChoiceLoader, DictLoader
from pytest_mock import MockerFixture

from flask_mongoengine.panels import MongoDebugPanel, _maybe_patch_jinja_loader


@pytest.fixture()
def app_no_mongo_monitoring():
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


@pytest.fixture
def registered_monitoring():
    """Register/Unregister mongo_command_logger in required tests"""
    from pymongo import monitoring

    from flask_mongoengine.panels import mongo_command_logger

    monitoring.register(mongo_command_logger)
    yield mongo_command_logger
    # Unregister listener between independent tests
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
    def toolbar_with_no_flask(self):
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
        assert toolbar_with_no_flask.is_properly_configured is False
        assert caplog.messages[0] == toolbar_with_no_flask.config_error_message

    def test__is_properly_configured__return_true__when_mongo_command_logger_registered(
        self,
        registered_monitoring,
        toolbar_with_no_flask,
    ):
        assert toolbar_with_no_flask.is_properly_configured is True

    def test__nav_subtitle__return_config_error_message__when_toolbar_incorrectly_configured(
        self, toolbar_with_no_flask
    ):
        """Also check that content flag changed."""
        # First line is before nav_subtitle() call
        assert toolbar_with_no_flask.has_content is True

        assert (
            toolbar_with_no_flask.nav_subtitle()
            == toolbar_with_no_flask.config_error_message
        )
        assert toolbar_with_no_flask.has_content is False

    def test__nav_subtitle__return_correct_message_when_toolbar_correctly_configured(
        self,
        registered_monitoring,
        toolbar_with_no_flask,
    ):
        assert toolbar_with_no_flask.nav_subtitle() == "0 operations, in  0.00ms"
        assert toolbar_with_no_flask.has_content is True

    def test__context__is_empty_by_default(self, app, toolbar_with_no_flask):
        assert toolbar_with_no_flask._context == {
            "queries": [],
            "inserts": [],
            "updates": [],
            "unknown": [],
            "deletes": [],
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
        registered_monitoring.inserts = [1, 2]
        registered_monitoring.updates = [1, 2]
        registered_monitoring.deletes = [1, 2]
        registered_monitoring.unknown = [1, 2]
        registered_monitoring.started_events = {1: 1, 2: 2}

        # Pre-test validation
        assert registered_monitoring.total_time == 1
        assert registered_monitoring.started_operations_count == 1
        assert registered_monitoring.succeeded_operations_count == 1
        assert registered_monitoring.failed_operations_count == 1
        assert registered_monitoring.queries == [1, 2]
        assert registered_monitoring.inserts == [1, 2]
        assert registered_monitoring.updates == [1, 2]
        assert registered_monitoring.deletes == [1, 2]
        assert registered_monitoring.unknown == [1, 2]
        assert registered_monitoring.started_events == {1: 1, 2: 2}
        toolbar_with_no_flask.process_request(None)

        assert id(registered_monitoring) == initial_id
        assert registered_monitoring.total_time == 0
        assert registered_monitoring.started_operations_count == 0
        assert registered_monitoring.succeeded_operations_count == 0
        assert registered_monitoring.failed_operations_count == 0
        assert registered_monitoring.queries == []
        assert registered_monitoring.inserts == []
        assert registered_monitoring.updates == []
        assert registered_monitoring.deletes == []
        assert registered_monitoring.unknown == []
        assert registered_monitoring.started_events == {}

    def test__content__calls_parent__render__function(
        self,
        app,
        registered_monitoring,
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

    pass

import pytest
from flask import session
from pytest_mock import MockerFixture

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
        return f'session: {session["a"]}'


@pytest.fixture
def permanent_session_app(app):
    @app.before_request
    def make_session_permanent():
        session.permanent = True

    return app


def test__save_session__called_on_session_set(app, mocker: MockerFixture):
    save_spy = mocker.spy(MongoEngineSessionInterface, "save_session")
    expiration_spy = mocker.spy(MongoEngineSessionInterface, "get_expiration_time")
    client = app.test_client()

    response = client.get("/")
    call_args, _ = expiration_spy.call_args_list[0]

    assert response.status_code == 200
    assert response.data.decode("utf-8") == "hello session"
    assert app.session_interface.cls.objects.count() == 1
    save_spy.assert_called_once()
    assert call_args[2].permanent is False  # session object


def test__save_session__called_on_session_set__should_respect_permanent_session_setting(
    permanent_session_app, mocker: MockerFixture
):
    expiration_spy = mocker.spy(MongoEngineSessionInterface, "get_expiration_time")
    client = permanent_session_app.test_client()
    client.get("/")

    call_args, _ = expiration_spy.call_args_list[0]
    assert call_args[2].permanent is True  # session object


def test__open_session_called_on_session_get(app, mocker: MockerFixture):
    client = app.test_client()
    open_spy = mocker.spy(MongoEngineSessionInterface, "open_session")
    client.get("/")
    open_spy.assert_called_once()  # On init call with no session

    response = client.get("/check-session")

    assert response.status_code == 200
    assert response.data.decode("utf-8") == "session: hello session"
    assert open_spy.call_count == 2  # On init + get with sid


@pytest.mark.parametrize("unsupported_value", (1, None, True, False, [], {}))
def test_session_interface__should_raise_value_error_if_collection_name_not_string(
    db, unsupported_value
):
    with pytest.raises(ValueError) as error:
        MongoEngineSessionInterface(db, collection=unsupported_value)

    assert str(error.value) == "Collection argument should be string"

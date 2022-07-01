"""Tests for base MongoEngine class."""
import pytest

from flask_mongoengine import MongoEngine


def test_mongoengine_class__should_raise_type_error__if_config_not_dict():
    """MongoEngine will handle None values, but will pass anything else as app."""
    input_value = "Not dict type"
    with pytest.raises(TypeError) as error:
        MongoEngine(input_value)
    assert str(error.value) == "Invalid Flask application instance"


@pytest.mark.parametrize("input_value", [None, "Not dict type"])
def test_init_app__should_raise_type_error__if_config_not_dict(input_value):
    db = MongoEngine()
    with pytest.raises(TypeError) as error:
        db.init_app(input_value)
    assert str(error.value) == "Invalid Flask application instance"

"""Tests for project wide decorators."""
from flask_mongoengine.decorators import orm_deprecated


def test__orm_deprecated(recwarn):
    @orm_deprecated
    def func(a, b):
        """Function example."""
        return a + b

    assert func(1, 1) == 2
    assert str(recwarn.list[0].message) == (
        "ORM module and function 'func' are deprecated and will be removed in version 3.0.0. "
        "Please switch to form generation from full model nesting. "
        "Support and bugfixes are not available for stalled code. "
        "Please read: "
    )

"""Strings and strings related fields demo model."""

from example_app.models import db


class BinaryDemoModel(db.Document):
    """Documentation example model."""

    string_field = db.StringField()
    binary_field = db.BinaryField()
    binary_field_with_default = db.BinaryField(default=lambda: "foobar".encode("utf-8"))
    file_field = db.FileField()


def binary_demo_view(pk=None):
    """Return all fields demonstration."""
    from example_app.views import demo_view

    return demo_view(model=BinaryDemoModel, view_name=binary_demo_view.__name__, pk=pk)

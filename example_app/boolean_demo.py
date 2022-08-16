"""Booleans fields demo model."""

from example_app.models import db


class BooleanDemoModel(db.Document):
    """Documentation example model."""

    simple_sting_name = db.StringField()
    boolean_field = db.BooleanField()
    boolean_field_with_null = db.BooleanField(null=True)
    true_boolean_field_with_allowed_null = db.BooleanField(null=True, default=True)
    boolean_field_with_as_choices_replace = db.BooleanField(
        wtf_options={
            "choices": [("", "Not selected"), ("yes", "Positive"), ("no", "Negative")]
        }
    )


BooleanDemoForm = BooleanDemoModel.to_wtf_form()


def boolean_demo_view(pk=None):
    """Return all fields demonstration."""
    from example_app.views import demo_view

    return demo_view(
        model=BooleanDemoModel, view_name=boolean_demo_view.__name__, pk=pk
    )

"""Numbers and related fields demo model."""

from decimal import Decimal

from example_app.models import db


class NumbersDemoModel(db.Document):
    """Documentation example model."""

    simple_sting_name = db.StringField()
    float_field_unlimited = db.FloatField()
    decimal_field_unlimited = db.DecimalField()
    integer_field_unlimited = db.IntField()
    float_field_limited = db.FloatField(min_value=float(1), max_value=200.455)
    decimal_field_limited = db.DecimalField(
        min_value=Decimal("1"), max_value=Decimal("200.455")
    )
    integer_field_limited = db.IntField(min_value=1, max_value=200)


NumbersDemoForm = NumbersDemoModel.to_wtf_form()


def numbers_demo_view(pk=None):
    """Return all fields demonstration."""
    from example_app.views import demo_view

    return demo_view(
        model=NumbersDemoModel, view_name=numbers_demo_view.__name__, pk=pk
    )

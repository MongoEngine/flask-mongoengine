"""Date and DateTime fields demo model."""

from wtforms.fields import DateTimeField

from example_app.models import db


class DateTimeModel(db.Document):
    """Documentation example model."""

    any_string = db.StringField()
    date = db.DateField()
    datetime = db.DateTimeField()
    datetime_no_sec = db.DateTimeField(wtf_options={"render_kw": {"step": "60"}})
    datetime_ms = db.DateTimeField(wtf_options={"render_kw": {"step": "0.001"}})
    complex_datetime = db.ComplexDateTimeField()
    complex_datetime_sec = db.ComplexDateTimeField(
        wtf_options={"render_kw": {"step": "1"}}
    )
    complex_datetime_microseconds = db.ComplexDateTimeField(
        wtf_field_class=DateTimeField, wtf_options={"format": "%Y-%m-%d %H:%M:%S.%f"}
    )


DateTimeDemoForm = DateTimeModel.to_wtf_form()


def dates_demo_view(pk=None):
    """Return all fields demonstration."""
    from example_app.views import demo_view

    return demo_view(model=DateTimeModel, view_name=dates_demo_view.__name__, pk=pk)

"""Date and DateTime fields demo model."""

from flask import render_template, request
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
    form = DateTimeDemoForm()
    obj = None
    if pk:
        obj = DateTimeModel.objects.get(pk=pk)
        form = DateTimeDemoForm(obj=obj)

    if request.method == "POST" and form.validate_on_submit():
        if pk:
            form.populate_obj(obj)
            obj.save()
        else:
            form.save()
    page_num = int(request.args.get("page") or 1)
    page = DateTimeModel.objects.paginate(page=page_num, per_page=100)

    return render_template(
        "form_demo.html",
        view=dates_demo_view.__name__,
        page=page,
        form=form,
        model=DateTimeModel,
    )

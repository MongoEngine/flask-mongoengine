"""Numbers and related fields demo model."""

from decimal import Decimal

from flask import render_template, request

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
    form = NumbersDemoForm()
    obj = None
    if pk:
        obj = NumbersDemoModel.objects.get(pk=pk)
        form = NumbersDemoForm(obj=obj)

    if request.method == "POST" and form.validate_on_submit():
        if pk:
            form.populate_obj(obj)
            obj.save()
        else:
            form.save()
    page_num = int(request.args.get("page") or 1)
    page = NumbersDemoModel.objects.paginate(page=page_num, per_page=100)

    return render_template(
        "numbers_demo.html", page=page, form=form, model=NumbersDemoModel
    )

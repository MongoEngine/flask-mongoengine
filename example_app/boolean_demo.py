"""Booleans fields demo model."""

from flask import render_template, request

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
    form = BooleanDemoForm()
    obj = None
    if pk:
        obj = BooleanDemoModel.objects.get(pk=pk)
        form = BooleanDemoForm(obj=obj)

    if request.method == "POST" and form.validate_on_submit():
        if pk:
            form.populate_obj(obj)
            obj.save()
        else:
            form.save()
    page_num = int(request.args.get("page") or 1)
    page = BooleanDemoModel.objects.paginate(page=page_num, per_page=100)

    return render_template(
        "form_demo.html",
        view=boolean_demo_view.__name__,
        page=page,
        form=form,
        model=BooleanDemoModel,
    )

"""Strings and strings related fields demo model."""
import re

from flask import render_template, request

from example_app.models import db
from flask_mongoengine.wtf import fields as mongo_fields


class StringsDemoModel(db.Document):
    """Documentation example model."""

    string_field = db.StringField()
    regexp_string_field = db.StringField(
        regex=re.compile(
            r"^(https:\/\/)[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+,;=]+$"
        )
    )
    sized_string_field = db.StringField(min_length=5)
    tel_field = db.StringField(wtf_field_class=mongo_fields.MongoTelField)
    password_field = db.StringField(
        wtf_field_class=mongo_fields.MongoPasswordField,
        required=True,
        min_length=5,
    )
    email_field = db.EmailField()
    url_field = db.URLField()


StringsDemoForm = StringsDemoModel.to_wtf_form()


def strings_demo_view(pk=None):
    """Return all fields demonstration."""
    form = StringsDemoForm()
    obj = None
    if pk:
        obj = StringsDemoModel.objects.get(pk=pk)
        form = StringsDemoForm(obj=obj)

    if request.method == "POST" and form.validate_on_submit():
        if pk:
            form.populate_obj(obj)
            obj.save()
        else:
            form.save()
    page_num = int(request.args.get("page") or 1)
    page = StringsDemoModel.objects.paginate(page=page_num, per_page=100)

    return render_template(
        "form_demo.html",
        view=strings_demo_view.__name__,
        page=page,
        form=form,
        model=StringsDemoModel,
    )

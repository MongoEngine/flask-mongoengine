"""Strings and strings related fields demo model."""
import re

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
    from example_app.views import demo_view

    return demo_view(
        model=StringsDemoModel, view_name=strings_demo_view.__name__, pk=pk
    )

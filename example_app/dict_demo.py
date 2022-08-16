"""Dict fields demo model."""

from example_app.models import db


def get_default_dict():
    """Example of default dict specification."""
    return {"alpha": 1, "text": "text", "float": 1.2}


class DictDemoModel(db.Document):
    """Documentation example model."""

    string = db.StringField(verbose_name="str")
    dict_field = db.DictField()
    no_dict_field = db.DictField(default=None)
    null_dict_field = db.DictField(default=None, null=True)
    dict_default = db.DictField(default=get_default_dict)
    null_dict_default = db.DictField(default=get_default_dict, null=True)
    no_dict_prefilled = db.DictField(
        default=None,
        null=False,
        wtf_options={"default": get_default_dict, "null": True},
    )


DictDemoForm = DictDemoModel.to_wtf_form()


def dict_demo_view(pk=None):
    """Return all fields demonstration."""
    from example_app.views import demo_view

    return demo_view(model=DictDemoModel, view_name=dict_demo_view.__name__, pk=pk)

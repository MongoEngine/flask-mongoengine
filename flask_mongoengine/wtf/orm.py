"""
Tools for generating forms based on mongoengine Document schemas.
"""
import decimal
from collections import OrderedDict
from typing import List, Optional, Type

from bson import ObjectId
from mongoengine import ReferenceField
from mongoengine.base import BaseDocument, DocumentMetaclass
from wtforms import fields as f
from wtforms import validators

from flask_mongoengine.decorators import orm_deprecated
from flask_mongoengine.wtf.fields import (
    BinaryField,
    DictField,
    ModelSelectField,
    ModelSelectMultipleField,
    NoneStringField,
)
from flask_mongoengine.wtf.models import ModelForm

__all__ = (
    "model_fields",
    "model_form",
)


@orm_deprecated
def converts(*args):
    def _inner(func):
        func._converter_for = frozenset(args)
        return func

    return _inner


class ModelConverter(object):
    @orm_deprecated
    def __init__(self, converters=None):
        if not converters:
            converters = {}

        for name in dir(self):
            obj = getattr(self, name)
            if hasattr(obj, "_converter_for"):
                for classname in obj._converter_for:
                    converters[classname] = obj

        self.converters = converters

    @orm_deprecated
    def _generate_convert_base_kwargs(self, field, field_args) -> dict:
        kwargs: dict = {
            "label": getattr(field, "verbose_name", field.name),
            "description": getattr(field, "help_text", None) or "",
            "validators": getattr(field, "wtf_validators", None)
            or getattr(field, "validators", None)
            or [],
            "filters": getattr(field, "wtf_filters", None)
            or getattr(field, "filters", None)
            or [],
            "default": field.default,
        }
        if field_args:
            kwargs.update(field_args)

        # Create a copy of the lists since we will be modifying it, and if
        # validators set as shared list between fields - duplicates/conflicts may
        # be created.
        kwargs["validators"] = list(kwargs["validators"])
        kwargs["filters"] = list(kwargs["filters"])
        if field.required:
            kwargs["validators"].append(validators.InputRequired())
        else:
            kwargs["validators"].append(validators.Optional())

        return kwargs

    @orm_deprecated
    def _process_convert_for_choice_fields(self, field, field_class, kwargs):
        kwargs["choices"] = field.choices
        kwargs["coerce"] = self.coerce(field_class)
        if kwargs.pop("multiple", False):
            return f.SelectMultipleField(**kwargs)
        if kwargs.pop("radio", False):
            return f.RadioField(**kwargs)
        return f.SelectField(**kwargs)

    @orm_deprecated
    def convert(self, model, field, field_args):
        field_class = type(field).__name__

        if field_class not in self.converters:
            return None

        kwargs = self._generate_convert_base_kwargs(field, field_args)

        if field.choices:
            return self._process_convert_for_choice_fields(field, field_class, kwargs)

        if hasattr(field, "field") and isinstance(field.field, ReferenceField):
            kwargs["label_modifier"] = getattr(
                model, f"{field.name}_label_modifier", None
            )

        return self.converters[field_class](model, field, kwargs)

    @classmethod
    def _string_common(cls, model, field, kwargs):
        if field.max_length or field.min_length:
            kwargs["validators"].append(
                validators.Length(
                    max=field.max_length or -1, min=field.min_length or -1
                )
            )

    @classmethod
    def _number_common(cls, model, field, kwargs):
        if field.max_value or field.min_value:
            kwargs["validators"].append(
                validators.NumberRange(max=field.max_value, min=field.min_value)
            )

    @converts("StringField")
    def conv_String(self, model, field, kwargs):
        if field.regex:
            kwargs["validators"].append(validators.Regexp(regex=field.regex))
        self._string_common(model, field, kwargs)
        password_field = kwargs.pop("password", False)
        textarea_field = kwargs.pop("textarea", False) or not field.max_length
        if password_field:
            return f.PasswordField(**kwargs)
        if textarea_field:
            return f.TextAreaField(**kwargs)
        return f.StringField(**kwargs)

    @converts("URLField")
    def conv_URL(self, model, field, kwargs):
        kwargs["validators"].append(validators.URL())
        self._string_common(model, field, kwargs)
        return NoneStringField(**kwargs)

    @converts("EmailField")
    def conv_Email(self, model, field, kwargs):
        kwargs["validators"].append(validators.Email())
        self._string_common(model, field, kwargs)
        return NoneStringField(**kwargs)

    @converts("IntField")
    def conv_Int(self, model, field, kwargs):
        self._number_common(model, field, kwargs)
        return f.IntegerField(**kwargs)

    @converts("FloatField")
    def conv_Float(self, model, field, kwargs):
        self._number_common(model, field, kwargs)
        return f.FloatField(**kwargs)

    @converts("DecimalField")
    def conv_Decimal(self, model, field, kwargs):
        self._number_common(model, field, kwargs)
        kwargs["places"] = getattr(field, "precision", None)
        return f.DecimalField(**kwargs)

    @converts("BooleanField")
    def conv_Boolean(self, model, field, kwargs):
        return f.BooleanField(**kwargs)

    @converts("DateTimeField")
    def conv_DateTime(self, model, field, kwargs):
        return f.DateTimeField(**kwargs)

    @converts("DateField")
    def conv_Date(self, model, field, kwargs):
        return f.DateField(**kwargs)

    @converts("BinaryField")
    def conv_Binary(self, model, field, kwargs):
        # TODO: may be set file field that will save file`s data to MongoDB
        if field.max_bytes:
            kwargs["validators"].append(validators.Length(max=field.max_bytes))
        return BinaryField(**kwargs)

    @converts("DictField")
    def conv_Dict(self, model, field, kwargs):
        return DictField(**kwargs)

    @converts("ListField")
    def conv_List(self, model, field, kwargs):
        if isinstance(field.field, ReferenceField):
            return ModelSelectMultipleField(model=field.field.document_type, **kwargs)
        if field.field.choices:
            kwargs["multiple"] = True
            return self.convert(model, field.field, kwargs)
        field_args = kwargs.pop("field_args", {})
        unbound_field = self.convert(model, field.field, field_args)
        unacceptable = {
            "validators": [],
            "filters": [],
            "min_entries": kwargs.get("min_entries", 0),
        }
        kwargs.update(unacceptable)
        return f.FieldList(unbound_field, **kwargs)

    @converts("SortedListField")
    def conv_SortedList(self, model, field, kwargs):
        # TODO: sort functionality, may be need sortable widget
        return self.conv_List(model, field, kwargs)

    @converts("GeoLocationField")
    def conv_GeoLocation(self, model, field, kwargs):
        # TODO: create geo field and widget (also GoogleMaps)
        return

    @converts("ObjectIdField")
    def conv_ObjectId(self, model, field, kwargs):
        return

    @converts("EmbeddedDocumentField")
    def conv_EmbeddedDocument(self, model, field, kwargs):
        kwargs = {
            "validators": [],
            "filters": [],
            "default": field.default or field.document_type_obj,
        }
        form_class = model_form(field.document_type_obj, field_args={})
        return f.FormField(form_class, **kwargs)

    @converts("ReferenceField")
    def conv_Reference(self, model, field, kwargs):
        return ModelSelectField(model=field.document_type, **kwargs)

    @converts("GenericReferenceField")
    def conv_GenericReference(self, model, field, kwargs):
        return

    @converts("FileField")
    def conv_File(self, model, field, kwargs):
        return f.FileField(**kwargs)

    @orm_deprecated
    def coerce(self, field_type):
        coercions = {
            "IntField": int,
            "BooleanField": bool,
            "FloatField": float,
            "DecimalField": decimal.Decimal,
            "ObjectIdField": ObjectId,
        }
        return coercions.get(field_type, str)


@orm_deprecated
def _get_fields_names(
    model,
    only: Optional[List[str]],
    exclude: Optional[List[str]],
) -> List[str]:
    """
    Filter fields names for further form generation.

    :param model: Source model class for fields list retrieval
    :param only: If provided, only these field names will have fields definition.
    :param exclude: If provided, field names will be excluded from fields definition.
      All other field names will have fields.
    """
    field_names = model._fields_ordered

    if only:
        field_names = [field for field in only if field in field_names]
    elif exclude:
        field_names = [field for field in field_names if field not in set(exclude)]

    return field_names


@orm_deprecated
def model_fields(
    model: Type[BaseDocument],
    only: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
    field_args=None,
    converter=None,
) -> OrderedDict:
    """
    Generate a dictionary of fields for a given database model.

    See :func:`model_form` docstring for description of parameters.
    """
    if not issubclass(model, (BaseDocument, DocumentMetaclass)):
        raise TypeError("model must be a mongoengine Document schema")

    converter = converter or ModelConverter()
    field_args = field_args or {}
    form_fields_dict = OrderedDict()
    # noinspection PyTypeChecker
    fields_names = _get_fields_names(model, only, exclude)

    for field_name in fields_names:
        # noinspection PyUnresolvedReferences
        model_field = model._fields[field_name]
        form_field = converter.convert(model, model_field, field_args.get(field_name))
        if form_field is not None:
            form_fields_dict[field_name] = form_field

    return form_fields_dict


@orm_deprecated
def model_form(
    model: Type[BaseDocument],
    base_class: Type[ModelForm] = ModelForm,
    only: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
    field_args=None,
    converter=None,
) -> Type[ModelForm]:
    """
    Create a wtforms Form for a given mongoengine Document schema::

        from flask_mongoengine.wtf import model_form
        from myproject.myapp.schemas import Article
        ArticleForm = model_form(Article)

    :param model:
        A mongoengine Document schema class
    :param base_class:
        Base form class to extend from. Must be a :class:`.ModelForm` subclass.
    :param only:
        An optional iterable with the property names that should be included in
        the form. Only these properties will have fields.
        Fields are always appear in provided order, this allows user to change form
        fields ordering, without changing database model.
    :param exclude:
        An optional iterable with the property names that should be excluded
        from the form. All other properties will have fields.
        Fields are appears in order, defined in model, excluding provided fields
        names. For adjusting fields ordering, use :attr:`only`.
    :param field_args:
        An optional dictionary of field names mapping to keyword arguments used
        to construct each field object.
    :param converter:
        A converter to generate the fields based on the model properties. If
        not set, :class:`.ModelConverter` is used.
    """
    field_dict = model_fields(model, only, exclude, field_args, converter)
    field_dict["model_class"] = model
    # noinspection PyTypeChecker
    return type(f"{model.__name__}Form", (base_class,), field_dict)

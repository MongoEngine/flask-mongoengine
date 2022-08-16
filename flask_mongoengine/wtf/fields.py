"""
Useful form fields for use with the mongoengine.
"""
__all__ = [
    "ModelSelectField",
    "QuerySetSelectField",
]
from typing import Callable, Optional

from flask import json
from mongoengine.queryset import DoesNotExist
from wtforms import fields as wtf_fields
from wtforms import validators as wtf_validators
from wtforms import widgets as wtf_widgets


def coerce_boolean(value: Optional[str]) -> Optional[bool]:
    """Transform SelectField boolean value from string and in reverse direction."""
    try:
        value = value.lower()
    except AttributeError:
        pass

    if value is None or value in {"", "none", "null"}:
        return None
    elif value is False or value in {"no", "n", "false"}:
        return False
    elif value is True or value in {"yes", "y", "true"}:
        return True
    else:
        raise ValueError("Unexpected string value.")


# noinspection PyAttributeOutsideInit,PyAbstractClass
class QuerySetSelectField(wtf_fields.SelectFieldBase):
    """
    Given a QuerySet either at initialization or inside a view, will display a
    select drop-down field of choices. The `data` property actually will
    store/keep an ORM model instance, not the ID. Submitting a choice which is
    not in the queryset will result in a validation error.

    Specifying `label_attr` in the constructor will use that property of the
    model instance for display in the list, else the model object's `__str__`
    or `__unicode__` will be used.

    If `allow_blank` is set to `True`, then a blank choice will be added to the
    top of the list. Selecting this choice will result in the `data` property
    being `None`.  The label for the blank choice can be set by specifying the
    `blank_text` parameter.
    """

    widget = wtf_widgets.Select()

    def __init__(
        self,
        label="",
        validators=None,
        queryset=None,
        label_attr="",
        allow_blank=False,
        blank_text="---",
        label_modifier=None,
        **kwargs,
    ):
        """Init docstring placeholder."""

        super(QuerySetSelectField, self).__init__(label, validators, **kwargs)
        self.label_attr = label_attr
        self.allow_blank = allow_blank
        self.blank_text = blank_text
        self.label_modifier = label_modifier
        self.queryset = queryset

    def iter_choices(self):
        """
        Provides data for choice widget rendering. Must return a sequence or
        iterable of (value, label, selected) tuples.
        """
        if self.allow_blank:
            yield "__None", self.blank_text, self.data is None

        if self.queryset is None:
            return

        self.queryset.rewind()
        for obj in self.queryset:
            label = (
                self.label_modifier(obj)
                if self.label_modifier
                else (self.label_attr and getattr(obj, self.label_attr) or obj)
            )

            if isinstance(self.data, list):
                selected = obj in self.data
            else:
                selected = self._is_selected(obj)
            yield obj.id, label, selected

    def process_formdata(self, valuelist):
        """
        Process data received over the wire from a form.

        This will be called during form construction with data supplied
        through the `formdata` argument.

        :param valuelist: A list of strings to process.
        """
        if not valuelist or valuelist[0] == "__None" or self.queryset is None:
            self.data = None
            return

        try:
            obj = self.queryset.get(pk=valuelist[0])
            self.data = obj
        except DoesNotExist:
            self.data = None

    def pre_validate(self, form):
        """
        Field-level validation. Runs before any other validators.

        :param form: The form the field belongs to.
        """
        if (not self.allow_blank or self.data is not None) and not self.data:
            raise wtf_validators.ValidationError(self.gettext("Not a valid choice"))

    def _is_selected(self, item):
        return item == self.data


# noinspection PyAttributeOutsideInit,PyAbstractClass
class QuerySetSelectMultipleField(QuerySetSelectField):
    """Same as :class:`QuerySetSelectField` but with multiselect options."""

    widget = wtf_widgets.Select(multiple=True)

    def __init__(
        self,
        label="",
        validators=None,
        queryset=None,
        label_attr="",
        allow_blank=False,
        blank_text="---",
        **kwargs,
    ):

        super(QuerySetSelectMultipleField, self).__init__(
            label, validators, queryset, label_attr, allow_blank, blank_text, **kwargs
        )

    def process_formdata(self, valuelist):
        """
        Process data received over the wire from a form.

        This will be called during form construction with data supplied
        through the `formdata` argument.

        :param valuelist: A list of strings to process.
        """

        if not valuelist or valuelist[0] == "__None" or not self.queryset:
            self.data = None
            return

        self.queryset.rewind()
        self.data = list(self.queryset(pk__in=valuelist))
        if not len(self.data):
            self.data = None

    def _is_selected(self, item):
        return item in self.data if self.data else False


# noinspection PyAttributeOutsideInit,PyAbstractClass
class ModelSelectField(QuerySetSelectField):
    """
    Like a QuerySetSelectField, except takes a model class instead of a
    queryset and lists everything in it.
    """

    def __init__(self, label="", validators=None, model=None, **kwargs):
        queryset = kwargs.pop("queryset", model.objects)
        super(ModelSelectField, self).__init__(
            label, validators, queryset=queryset, **kwargs
        )


# noinspection PyAttributeOutsideInit,PyAbstractClass
class ModelSelectMultipleField(QuerySetSelectMultipleField):
    """
    Allows multiple select
    """

    def __init__(self, label="", validators=None, model=None, **kwargs):
        queryset = kwargs.pop("queryset", model.objects)
        super(ModelSelectMultipleField, self).__init__(
            label, validators, queryset=queryset, **kwargs
        )


# noinspection PyAttributeOutsideInit,PyAbstractClass
class JSONField(wtf_fields.TextAreaField):
    """Special version fo :class:`wtforms.fields.TextAreaField`."""

    def _value(self):
        # TODO: Investigate why raw mentioned.
        if self.raw_data:
            return self.raw_data[0]
        else:
            return self.data and json.dumps(self.data) or ""

    def process_formdata(self, valuelist):
        """
        Process data received over the wire from a form.

        This will be called during form construction with data supplied
        through the `formdata` argument.

        :param valuelist: A list of strings to process.
        """
        if valuelist:
            try:
                self.data = json.loads(valuelist[0])
            except ValueError as error:
                raise ValueError(self.gettext("Invalid JSON data.")) from error


class DictField(JSONField):
    """
    Special version fo :class:`JSONField` to be generated for
    :class:`flask_mongoengine.db_fields.DictField`.

    Used in generator before flask_mongoengine version 2.0
    """

    def process_formdata(self, valuelist):
        """
        Process data received over the wire from a form.

        This will be called during form construction with data supplied
        through the `formdata` argument.

        :param valuelist: A list of strings to process.
        """
        super(DictField, self).process_formdata(valuelist)
        if valuelist and not isinstance(self.data, dict):
            raise ValueError(self.gettext("Not a valid dictionary."))


# noinspection PyAttributeOutsideInit
class NoneStringField(wtf_fields.StringField):
    """
    Custom StringField that counts "" as None
    """

    def process_formdata(self, valuelist):
        """
        Process data received over the wire from a form.

        This will be called during form construction with data supplied
        through the `formdata` argument.

        :param valuelist: A list of strings to process.
        """
        if valuelist:
            self.data = valuelist[0]
        if self.data == "":
            self.data = None


# noinspection PyAttributeOutsideInit
class BinaryField(wtf_fields.TextAreaField):
    """
    Custom TextAreaField that converts its value with binary_type.
    """

    def process_formdata(self, valuelist):
        """
        Process data received over the wire from a form.

        This will be called during form construction with data supplied
        through the `formdata` argument.

        :param valuelist: A list of strings to process.
        """
        if valuelist:
            self.data = bytes(valuelist[0], "utf-8")


# noinspection PyUnresolvedReferences,PyAttributeOutsideInit
class EmptyStringIsNoneMixin:
    """
    Special mixin to ignore empty strings **before** parent class processing.

    Unlike old :class:`NoneStringField` we do it before parent class call, this allows
    us to reuse this mixin in many more cases without errors.
    """

    def process_formdata(self, valuelist):
        """
        Ignores empty string and calls parent :func:`process_formdata` if data present.

        :param valuelist: A list of strings to process.
        """
        if not valuelist or valuelist[0] == "":
            self.data = None
        else:
            super().process_formdata(valuelist)


class MongoBooleanField(wtf_fields.SelectField):
    """Mongo SelectField field for BooleanFields, that correctly coerce values."""

    def __init__(
        self,
        label=None,
        validators=None,
        coerce=None,
        choices=None,
        validate_choice=True,
        **kwargs,
    ):
        """
        Replaces defaults of :class:`wtforms.fields.SelectField` with for Boolean values.

        Fully compatible with :class:`wtforms.fields.SelectField` and have same parameters.


        """
        if coerce is None:
            coerce = coerce_boolean
        if choices is None:
            choices = [("", "---"), ("yes", "yes"), ("no", "no")]

        super().__init__(
            label=label,
            validators=validators,
            coerce=coerce,
            choices=choices,
            validate_choice=validate_choice,
            **kwargs,
        )


class MongoEmailField(EmptyStringIsNoneMixin, wtf_fields.EmailField):
    """
    Regular :class:`wtforms.fields.EmailField`, that transform empty string to `None`.
    """

    pass


class MongoHiddenField(EmptyStringIsNoneMixin, wtf_fields.HiddenField):
    """
    Regular :class:`wtforms.fields.HiddenField`, that transform empty string to `None`.
    """

    pass


class MongoPasswordField(EmptyStringIsNoneMixin, wtf_fields.PasswordField):
    """
    Regular :class:`wtforms.fields.PasswordField`, that transform empty string to `None`.
    """

    pass


class MongoSearchField(EmptyStringIsNoneMixin, wtf_fields.SearchField):
    """
    Regular :class:`wtforms.fields.SearchField`, that transform empty string to `None`.
    """

    pass


class MongoStringField(EmptyStringIsNoneMixin, wtf_fields.StringField):
    """
    Regular :class:`wtforms.fields.StringField`, that transform empty string to `None`.
    """

    pass


class MongoTelField(EmptyStringIsNoneMixin, wtf_fields.TelField):
    """
    Regular :class:`wtforms.fields.TelField`, that transform empty string to `None`.
    """

    pass


class MongoTextAreaField(EmptyStringIsNoneMixin, wtf_fields.TextAreaField):
    """
    Regular :class:`wtforms.fields.TextAreaField`, that transform empty string to `None`.
    """

    pass


class MongoURLField(EmptyStringIsNoneMixin, wtf_fields.URLField):
    """
    Regular :class:`wtforms.fields.URLField`, that transform empty string to `None`.
    """

    pass


class MongoFloatField(wtf_fields.FloatField):
    """
    Regular :class:`wtforms.fields.FloatField`, with widget replaced to
    :class:`wtforms.widgets.NumberInput`.
    """

    widget = wtf_widgets.NumberInput(step="any")


class MongoDictField(MongoTextAreaField):
    """Form field to handle JSON in :class:`~flask_mongoengine.db_fields.DictField`."""

    def __init__(
        self,
        json_encoder: Optional[Callable] = None,
        json_encoder_kwargs: Optional[dict] = None,
        json_decoder: Optional[Callable] = None,
        json_decoder_kwargs: Optional[dict] = None,
        null: Optional[bool] = None,
        *args,
        **kwargs,
    ):
        """
        Special WTForms field for :class:`~flask_mongoengine.db_fields.DictField`

        Configuration available with providing :attr:`wtf_options` on
        :class:`~flask_mongoengine.db_fields.DictField` initialization.

        :param json_encoder: Any function, capable to transform dict to string, by
            default :func:`json.dumps`
        :param json_encoder_kwargs: Any dictionary with parameters to
            :func:`json_encoder`, by default: `{"indent":4}`
        :param json_decoder: Any function, capable to transform string to dict, by
            default :func:`json.loads`
        :param json_decoder_kwargs: Any dictionary with parameters to
            :func:`json_decoder`, by default: `{}`
        """

        self.json_encoder = json_encoder or json.dumps
        self.json_encoder_kwargs = json_encoder_kwargs or {"indent": 4}
        self.json_decoder = json_decoder or json.loads
        self.json_decoder_kwargs = json_decoder_kwargs or {}
        self.data = None
        self.null = null
        super().__init__(*args, **kwargs)
        try:
            self._default = self.default()
        except TypeError:
            self._default = self.default
        if isinstance(self._default, dict):
            self._default = self.json_encoder(self._default, **self.json_encoder_kwargs)

    def _parse_json_data(self):
        """Tries to load JSON data with python internal JSON library."""
        try:
            self.data = self.json_decoder(self.data, **self.json_decoder_kwargs)
        except ValueError as error:
            raise wtf_validators.ValidationError(
                self.gettext(f"Cannot load data: {error}")
            ) from error

    def _ensure_data_is_dict(self):
        """Ensures that saved data is dict, not a list or other valid parsed JSON."""
        if not isinstance(self.data, dict):
            raise wtf_validators.ValidationError(
                self.gettext("Not a valid dictionary (list input detected).")
            )

    def process_formdata(self, valuelist):
        """Process text form data to dictionary or raise JSONDecodeError."""
        super().process_formdata(valuelist)
        if self.data is not None:
            self._parse_json_data()
            self._ensure_data_is_dict()

    def _value(self):
        """Show existing data as pretty-formatted, or show raw data/empty dict."""
        if self.data is not None:
            return (
                self.json_encoder(self.data, **self.json_encoder_kwargs)
                if isinstance(self.data, dict)
                else self.data
            )
        return self._default if self._default is not None and not self.null else ""

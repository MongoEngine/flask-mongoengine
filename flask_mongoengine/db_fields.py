"""Responsible for mongoengine fields extension, if WTFForms integration used."""
__all__ = [
    "WtfFieldMixin",
    "BinaryField",
    "BooleanField",
    "CachedReferenceField",
    "ComplexDateTimeField",
    "DateField",
    "DateTimeField",
    "DecimalField",
    "DictField",
    "DynamicField",
    "EmailField",
    "EmbeddedDocumentField",
    "EmbeddedDocumentListField",
    "EnumField",
    "FileField",
    "FloatField",
    "GenericEmbeddedDocumentField",
    "GenericLazyReferenceField",
    "GenericReferenceField",
    "GeoJsonBaseField",
    "GeoPointField",
    "ImageField",
    "IntField",
    "LazyReferenceField",
    "LineStringField",
    "ListField",
    "LongField",
    "MapField",
    "MultiLineStringField",
    "MultiPointField",
    "MultiPolygonField",
    "ObjectIdField",
    "PointField",
    "PolygonField",
    "ReferenceField",
    "SequenceField",
    "SortedListField",
    "StringField",
    "URLField",
    "UUIDField",
]
import decimal
import warnings
from typing import Callable, List, Optional, Type, Union

from bson import ObjectId
from mongoengine import fields

from flask_mongoengine.decorators import wtf_required

try:
    from wtforms import fields as wtf_fields
    from wtforms import validators as wtf_validators_

    from flask_mongoengine.wtf import fields as custom_fields
except ImportError:  # pragma: no cover
    custom_fields = None
    wtf_fields = None
    wtf_validators_ = None


@wtf_required
def _setup_strings_common_validators(options: dict, obj: fields.StringField) -> dict:
    """
    Extend :attr:`base_options` with common validators for string types.

    :param options: dict, usually from :class:`WtfFieldMixin.wtf_generated_options`
    :param obj: Any :class:`mongoengine.fields.StringField` subclass instance.
    """
    assert isinstance(obj, fields.StringField), "Improperly configured"
    if obj.min_length or obj.max_length:
        options["validators"].insert(
            0,
            wtf_validators_.Length(
                min=obj.min_length or -1,
                max=obj.max_length or -1,
            ),
        )

    if obj.regex:
        options["validators"].insert(0, wtf_validators_.Regexp(regex=obj.regex))

    return options


@wtf_required
def _setup_numbers_common_validators(
    options: dict, obj: Union[fields.IntField, fields.DecimalField, fields.FloatField]
) -> dict:
    """
    Extend :attr:`base_options` with common validators for number types.

    :param options: dict, usually from :class:`WtfFieldMixin.wtf_generated_options`
    :param obj: Any :class:`mongoengine.fields.IntField` or
        :class:`mongoengine.fields.DecimalField` or
        :class:`mongoengine.fields.FloatField` subclasses instance.
    """
    assert isinstance(
        obj, (fields.IntField, fields.DecimalField, fields.FloatField)
    ), "Improperly configured"

    if obj.min_value or obj.max_value:
        options["validators"].insert(
            0, wtf_validators_.NumberRange(min=obj.min_value, max=obj.max_value)
        )

    return options


class WtfFieldMixin:
    """
    Extension wrapper class for mongoengine BaseField.

    This enables flask-mongoengine wtf to extend the number of field parameters, and
    settings on behalf of document model form generator for WTForm.

    **Class variables:**

    :cvar DEFAULT_WTF_CHOICES_FIELD: Default WTForms Field used for db fields when
        **choices** option specified.
    :cvar DEFAULT_WTF_FIELD: Default WTForms Field used for db field.
    """

    DEFAULT_WTF_FIELD = None
    DEFAULT_WTF_CHOICES_FIELD = wtf_fields.SelectField if wtf_fields else None
    DEFAULT_WTF_CHOICES_COERCE = str

    def __init__(
        self,
        *,
        validators: Optional[Union[List, Callable]] = None,
        filters: Optional[Union[List, Callable]] = None,
        wtf_field_class: Optional[Type] = None,
        wtf_filters: Optional[Union[List, Callable]] = None,
        wtf_validators: Optional[Union[List, Callable]] = None,
        wtf_choices_coerce: Optional[Callable] = None,
        wtf_options: Optional[dict] = None,
        **kwargs,
    ):
        """
        Extended :func:`__init__` method for mongoengine db field with WTForms options.

        :param filters:     DEPRECATED: wtf form field filters.
        :param validators:  DEPRECATED: wtf form field validators.
        :param wtf_field_class: Any subclass of :class:`wtforms.forms.core.Field` that
            can be used for form field generation. Takes precedence over
            :attr:`DEFAULT_WTF_FIELD`  and :attr:`DEFAULT_WTF_CHOICES_FIELD`
        :param wtf_filters:     wtf form field filters.
        :param wtf_validators:  wtf form field validators.
        :param wtf_choices_coerce: Callable function to replace
            :attr:`DEFAULT_WTF_CHOICES_COERCE` for choices fields.
        :param wtf_options: Dictionary with WTForm Field settings.
            Applied last, takes precedence over any generated field options.
        :param kwargs: keyword arguments silently bypassed to normal mongoengine fields
        """
        if validators is not None:
            warnings.warn(
                (
                    "Passing 'validators' keyword argument to field definition is "
                    "deprecated and will be removed in version 3.0.0. "
                    "Please rename 'validators' to 'wtf_validators'. "
                    "If both values set, 'wtf_validators' is used."
                ),
                DeprecationWarning,
                stacklevel=2,
            )
        if filters is not None:
            warnings.warn(
                (
                    "Passing 'filters' keyword argument to field definition is "
                    "deprecated and will be removed in version 3.0.0. "
                    "Please rename 'filters' to 'wtf_filters'. "
                    "If both values set, 'wtf_filters' is used."
                ),
                DeprecationWarning,
                stacklevel=2,
            )
        self.wtf_validators = self._ensure_callable_or_list(
            wtf_validators or validators, "wtf_validators"
        )
        self.wtf_filters = self._ensure_callable_or_list(
            wtf_filters or filters, "wtf_filters"
        )
        self.wtf_options = wtf_options
        self.wtf_choices_coerce = wtf_choices_coerce or self.DEFAULT_WTF_CHOICES_COERCE
        # Some attributes that will be updated by super()
        self.required = False
        self.default = None
        self.name = ""
        self.choices = None

        # Internals
        self._wtf_field_class = wtf_field_class

        super().__init__(**kwargs)

    @property
    def wtf_field_class(self) -> Type:
        """Final WTForm Field class, that will be used for field generation."""
        if self._wtf_field_class:
            return self._wtf_field_class
        if self.choices and self.DEFAULT_WTF_CHOICES_FIELD:
            return self.DEFAULT_WTF_CHOICES_FIELD
        return self.DEFAULT_WTF_FIELD

    @property
    @wtf_required
    def wtf_generated_options(self) -> dict:
        """
        WTForm Field options generated by class, not updated by user provided :attr:`wtf_options`.
        """
        wtf_field_kwargs: dict = {
            "label": getattr(self, "verbose_name", self.name),
            "description": getattr(self, "help_text", None) or "",
            "default": self.default,
            # Create a copy of the lists with list() call, since we will be modifying it
            "validators": list(self.wtf_validators) or [],
            "filters": list(self.wtf_filters) or [],
        }

        if self.required:
            wtf_field_kwargs["validators"].append(wtf_validators_.InputRequired())
        else:
            wtf_field_kwargs["validators"].append(wtf_validators_.Optional())

        if self.choices:
            wtf_field_kwargs["choices"] = self.choices
            wtf_field_kwargs["coerce"] = self.wtf_choices_coerce

        return wtf_field_kwargs

    @property
    @wtf_required
    def wtf_field_options(self) -> dict:
        """
        Final WTForm Field options that will be applied as :attr:`wtf_field_class` kwargs.

        Can be overwritten by :func:`to_wtf_field` if
        :func:`~flask_mongoengine.documents.WtfFormMixin.to_wtf_form` called with related
        field name in :attr:`fields_kwargs`.

        It is not recommended to overwrite this property, for logic update overwrite
        :attr:`wtf_generated_options`
        """
        wtf_field_kwargs = self.wtf_generated_options
        if self.wtf_options is not None:
            wtf_field_kwargs.update(self.wtf_options)

        return wtf_field_kwargs

    @staticmethod
    def _ensure_callable_or_list(argument, msg_flag: str) -> Optional[List]:
        """
        Ensure submitted argument value is a callable object or valid list value.

        :param argument: Argument input to make verification on.
        :param msg_flag: Argument string name for error message.
        """
        if argument is None:
            return []

        if callable(argument):
            return [argument]
        elif not isinstance(argument, list):
            raise TypeError(f"Argument '{msg_flag}' must be a list value")

        return argument

    def to_wtf_field(
        self,
        *,
        model: Optional[Type] = None,
        field_kwargs: Optional[dict] = None,
    ):
        """
        Default WTFFormField generator for most of the fields.

        :param model:
            Document of model from :mod:`~flask_mongoengine.documents`, passed by
            :func:`~flask_mongoengine.documents.WtfFormMixin.to_wtf_form` for field
            types with other Document type dependency signature compatibility.
        :param field_kwargs:
            Final field generation adjustments, passed for custom Forms generation from
            :func:`~flask_mongoengine.documents.WtfFormMixin.to_wtf_form`
            :attr:`fields_kwargs` parameter.
        """
        field_kwargs = field_kwargs or {}
        wtf_field_kwargs = self.wtf_field_options
        wtf_field_class = (
            field_kwargs.pop("wtf_field_class", None) or self.wtf_field_class
        )
        if field_kwargs:
            wtf_field_kwargs.update(field_kwargs)

        return wtf_field_class(**wtf_field_kwargs)


class BinaryField(WtfFieldMixin, fields.BinaryField):
    """
    Extends :class:`mongoengine.fields.BinaryField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    DEFAULT_WTF_FIELD = custom_fields.BinaryField if custom_fields else None

    def to_wtf_field(
        self,
        *,
        model: Optional[Type] = None,
        field_kwargs: Optional[dict] = None,
    ):
        """
        Protection from execution of :func:`to_wtf_field` in form generation.

        :raises NotImplementedError: Field converter to WTForm Field not implemented.
        """
        raise NotImplementedError("Field converter to WTForm Field not implemented.")


class BooleanField(WtfFieldMixin, fields.BooleanField):
    """
    Extends :class:`mongoengine.fields.BooleanField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    DEFAULT_WTF_FIELD = custom_fields.MongoBooleanField if custom_fields else None


class CachedReferenceField(WtfFieldMixin, fields.CachedReferenceField):
    """
    Extends :class:`mongoengine.fields.CachedReferenceField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    def to_wtf_field(
        self,
        *,
        model: Optional[Type] = None,
        field_kwargs: Optional[dict] = None,
    ):
        """
        Protection from execution of :func:`to_wtf_field` in form generation.

        :raises NotImplementedError: Field converter to WTForm Field not implemented.
        """
        raise NotImplementedError("Field converter to WTForm Field not implemented.")


class ComplexDateTimeField(WtfFieldMixin, fields.ComplexDateTimeField):
    """
    Extends :class:`mongoengine.fields.ComplexDateTimeField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.

    .. important::
        During WTForm generation this field uses :class:`wtforms.fields.DateTimeLocalField`
        with milliseconds accuracy. Direct microseconds not supported by browsers for
        this type of field. If exact microseconds support required, please use
        :class:`wtforms.fields.DateTimeField` with extended text format set. Examples
        available in example app.

        This does not affect on in database accuracy.
    """

    DEFAULT_WTF_FIELD = wtf_fields.DateTimeLocalField if wtf_fields else None

    @property
    @wtf_required
    def wtf_generated_options(self) -> dict:
        """Extend form date time field with milliseconds support."""
        options = super().wtf_generated_options
        options["format"] = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S.%f",
        ]
        options["render_kw"] = {"step": "0.000001"}

        return options


class DateField(WtfFieldMixin, fields.DateField):
    """
    Extends :class:`mongoengine.fields.DateField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    DEFAULT_WTF_FIELD = wtf_fields.DateField if wtf_fields else None


class DateTimeField(WtfFieldMixin, fields.DateTimeField):
    """
    Extends :class:`mongoengine.fields.DateTimeField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    DEFAULT_WTF_FIELD = wtf_fields.DateTimeLocalField if wtf_fields else None

    @property
    @wtf_required
    def wtf_generated_options(self) -> dict:
        """Extend form date time field with milliseconds support."""
        options = super().wtf_generated_options
        options["format"] = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S.%f",
        ]
        options["render_kw"] = {"step": "1"}

        return options


class DecimalField(WtfFieldMixin, fields.DecimalField):
    """
    Extends :class:`mongoengine.fields.DecimalField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    DEFAULT_WTF_FIELD = wtf_fields.DecimalField if wtf_fields else None
    DEFAULT_WTF_CHOICES_COERCE = decimal.Decimal

    @property
    @wtf_required
    def wtf_generated_options(self) -> dict:
        """
        Extend form validators with :class:`wtforms.validators.NumberRange`.
        """
        options = super().wtf_generated_options
        options = _setup_numbers_common_validators(options, self)

        return options


class DictField(WtfFieldMixin, fields.DictField):
    """
    Extends :class:`mongoengine.fields.DictField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    DEFAULT_WTF_FIELD = custom_fields.MongoDictField if custom_fields else None

    @property
    def wtf_generated_options(self) -> dict:
        """Extends default field options with `null` bypass."""
        options = super().wtf_generated_options
        options["null"] = self.null
        return options


class DynamicField(WtfFieldMixin, fields.DynamicField):
    """
    Extends :class:`mongoengine.fields.DynamicField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    def to_wtf_field(
        self,
        *,
        model: Optional[Type] = None,
        field_kwargs: Optional[dict] = None,
    ):
        """
        Protection from execution of :func:`to_wtf_field` in form generation.

        :raises NotImplementedError: Field converter to WTForm Field not implemented.
        """
        raise NotImplementedError("Field converter to WTForm Field not implemented.")


class EmailField(WtfFieldMixin, fields.EmailField):
    """
    Extends :class:`mongoengine.fields.EmailField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.

    .. versionchanged:: 2.0.0
        Default form field output changed from :class:`.NoneStringField` to
        :class:`flask_mongoengine.wtf.fields.MongoEmailField`
    """

    DEFAULT_WTF_FIELD = custom_fields.MongoEmailField if custom_fields else None

    @property
    @wtf_required
    def wtf_generated_options(self) -> dict:
        """Extend form validators with :class:`wtforms.validators.Email`"""
        options = super().wtf_generated_options
        options = _setup_strings_common_validators(options, self)
        options["validators"].insert(0, wtf_validators_.Email())

        return options


class EmbeddedDocumentField(WtfFieldMixin, fields.EmbeddedDocumentField):
    """
    Extends :class:`mongoengine.fields.EmbeddedDocumentField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    DEFAULT_WTF_FIELD = wtf_fields.FormField if wtf_fields else None

    def to_wtf_field(
        self,
        *,
        model: Optional[Type] = None,
        field_kwargs: Optional[dict] = None,
    ):
        """
        Protection from execution of :func:`to_wtf_field` in form generation.

        :raises NotImplementedError: Field converter to WTForm Field not implemented.
        """
        raise NotImplementedError("Field converter to WTForm Field not implemented.")


class EmbeddedDocumentListField(WtfFieldMixin, fields.EmbeddedDocumentListField):
    """
    Extends :class:`mongoengine.fields.EmbeddedDocumentListField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    def to_wtf_field(
        self,
        *,
        model: Optional[Type] = None,
        field_kwargs: Optional[dict] = None,
    ):
        """
        Protection from execution of :func:`to_wtf_field` in form generation.

        :raises NotImplementedError: Field converter to WTForm Field not implemented.
        """
        raise NotImplementedError("Field converter to WTForm Field not implemented.")


class EnumField(WtfFieldMixin, fields.EnumField):
    """
    Extends :class:`mongoengine.fields.EnumField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    def to_wtf_field(
        self,
        *,
        model: Optional[Type] = None,
        field_kwargs: Optional[dict] = None,
    ):
        """
        Protection from execution of :func:`to_wtf_field` in form generation.

        :raises NotImplementedError: Field converter to WTForm Field not implemented.
        """
        raise NotImplementedError("Field converter to WTForm Field not implemented.")


class FileField(WtfFieldMixin, fields.FileField):
    """
    Extends :class:`mongoengine.fields.FileField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    DEFAULT_WTF_FIELD = wtf_fields.FileField if wtf_fields else None

    def to_wtf_field(
        self,
        *,
        model: Optional[Type] = None,
        field_kwargs: Optional[dict] = None,
    ):
        """
        Protection from execution of :func:`to_wtf_field` in form generation.

        :raises NotImplementedError: Field converter to WTForm Field not implemented.
        """
        raise NotImplementedError("Field converter to WTForm Field not implemented.")


class FloatField(WtfFieldMixin, fields.FloatField):
    """
    Extends :class:`mongoengine.fields.FloatField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.

    .. versionchanged:: 2.0.0
        Default form field output changed from :class:`wtforms.fields.FloatField` to
        :class:`flask_mongoengine.wtf.fields.MongoFloatField` with 'numbers' input type.
    """

    DEFAULT_WTF_FIELD = custom_fields.MongoFloatField if wtf_fields else None
    DEFAULT_WTF_CHOICES_COERCE = float

    @property
    @wtf_required
    def wtf_generated_options(self) -> dict:
        """
        Extend form validators with :class:`wtforms.validators.NumberRange`.
        """
        options = super().wtf_generated_options
        options = _setup_numbers_common_validators(options, self)

        return options


class GenericEmbeddedDocumentField(WtfFieldMixin, fields.GenericEmbeddedDocumentField):
    """
    Extends :class:`mongoengine.fields.GenericEmbeddedDocumentField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    def to_wtf_field(
        self,
        *,
        model: Optional[Type] = None,
        field_kwargs: Optional[dict] = None,
    ):
        """
        Protection from execution of :func:`to_wtf_field` in form generation.

        :raises NotImplementedError: Field converter to WTForm Field not implemented.
        """
        raise NotImplementedError("Field converter to WTForm Field not implemented.")


class GenericLazyReferenceField(WtfFieldMixin, fields.GenericLazyReferenceField):
    """
    Extends :class:`mongoengine.fields.GenericLazyReferenceField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    def to_wtf_field(
        self,
        *,
        model: Optional[Type] = None,
        field_kwargs: Optional[dict] = None,
    ):
        """
        Protection from execution of :func:`to_wtf_field` in form generation.

        :raises NotImplementedError: Field converter to WTForm Field not implemented.
        """
        raise NotImplementedError("Field converter to WTForm Field not implemented.")


class GenericReferenceField(WtfFieldMixin, fields.GenericReferenceField):
    """
    Extends :class:`mongoengine.fields.GenericReferenceField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    def to_wtf_field(
        self,
        *,
        model: Optional[Type] = None,
        field_kwargs: Optional[dict] = None,
    ):
        """
        Protection from execution of :func:`to_wtf_field` in form generation.

        :raises NotImplementedError: Field converter to WTForm Field not implemented.
        """
        raise NotImplementedError("Field converter to WTForm Field not implemented.")


class GeoJsonBaseField(WtfFieldMixin, fields.GeoJsonBaseField):
    """
    Extends :class:`mongoengine.fields.GeoJsonBaseField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    def to_wtf_field(
        self,
        *,
        model: Optional[Type] = None,
        field_kwargs: Optional[dict] = None,
    ):
        """
        Protection from execution of :func:`to_wtf_field` in form generation.

        :raises NotImplementedError: Field converter to WTForm Field not implemented.
        """
        raise NotImplementedError("Field converter to WTForm Field not implemented.")


class GeoPointField(WtfFieldMixin, fields.GeoPointField):
    """
    Extends :class:`mongoengine.fields.GeoPointField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    def to_wtf_field(
        self,
        *,
        model: Optional[Type] = None,
        field_kwargs: Optional[dict] = None,
    ):
        """
        Protection from execution of :func:`to_wtf_field` in form generation.

        :raises NotImplementedError: Field converter to WTForm Field not implemented.
        """
        raise NotImplementedError("Field converter to WTForm Field not implemented.")


class ImageField(WtfFieldMixin, fields.ImageField):
    """
    Extends :class:`mongoengine.fields.ImageField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    def to_wtf_field(
        self,
        *,
        model: Optional[Type] = None,
        field_kwargs: Optional[dict] = None,
    ):
        """
        Protection from execution of :func:`to_wtf_field` in form generation.

        :raises NotImplementedError: Field converter to WTForm Field not implemented.
        """
        raise NotImplementedError("Field converter to WTForm Field not implemented.")


class IntField(WtfFieldMixin, fields.IntField):
    """
    Extends :class:`mongoengine.fields.IntField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    DEFAULT_WTF_FIELD = wtf_fields.IntegerField if wtf_fields else None
    DEFAULT_WTF_CHOICES_COERCE = int

    @property
    @wtf_required
    def wtf_generated_options(self) -> dict:
        """
        Extend form validators with :class:`wtforms.validators.NumberRange`.
        """
        options = super().wtf_generated_options
        options = _setup_numbers_common_validators(options, self)

        return options


class LazyReferenceField(WtfFieldMixin, fields.LazyReferenceField):
    """
    Extends :class:`mongoengine.fields.LazyReferenceField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    def to_wtf_field(
        self,
        *,
        model: Optional[Type] = None,
        field_kwargs: Optional[dict] = None,
    ):
        """
        Protection from execution of :func:`to_wtf_field` in form generation.

        :raises NotImplementedError: Field converter to WTForm Field not implemented.
        """
        raise NotImplementedError("Field converter to WTForm Field not implemented.")


class LineStringField(WtfFieldMixin, fields.LineStringField):
    """
    Extends :class:`mongoengine.fields.LineStringField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    def to_wtf_field(
        self,
        *,
        model: Optional[Type] = None,
        field_kwargs: Optional[dict] = None,
    ):
        """
        Protection from execution of :func:`to_wtf_field` in form generation.

        :raises NotImplementedError: Field converter to WTForm Field not implemented.
        """
        raise NotImplementedError("Field converter to WTForm Field not implemented.")


class ListField(WtfFieldMixin, fields.ListField):
    """
    Extends :class:`mongoengine.fields.ListField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    DEFAULT_WTF_FIELD = wtf_fields.FieldList if wtf_fields else None

    def to_wtf_field(
        self,
        *,
        model: Optional[Type] = None,
        field_kwargs: Optional[dict] = None,
    ):
        """
        Protection from execution of :func:`to_wtf_field` in form generation.

        :raises NotImplementedError: Field converter to WTForm Field not implemented.
        """
        raise NotImplementedError("Field converter to WTForm Field not implemented.")


class LongField(WtfFieldMixin, fields.LongField):
    """
    Extends :class:`mongoengine.fields.LongField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    def to_wtf_field(
        self,
        *,
        model: Optional[Type] = None,
        field_kwargs: Optional[dict] = None,
    ):
        """
        Protection from execution of :func:`to_wtf_field` in form generation.

        :raises NotImplementedError: Field converter to WTForm Field not implemented.
        """
        raise NotImplementedError("Field converter to WTForm Field not implemented.")


class MapField(WtfFieldMixin, fields.MapField):
    """
    Extends :class:`mongoengine.fields.MapField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    def to_wtf_field(
        self,
        *,
        model: Optional[Type] = None,
        field_kwargs: Optional[dict] = None,
    ):
        """
        Protection from execution of :func:`to_wtf_field` in form generation.

        :raises NotImplementedError: Field converter to WTForm Field not implemented.
        """
        raise NotImplementedError("Field converter to WTForm Field not implemented.")


class MultiLineStringField(WtfFieldMixin, fields.MultiLineStringField):
    """
    Extends :class:`mongoengine.fields.MultiLineStringField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    def to_wtf_field(
        self,
        *,
        model: Optional[Type] = None,
        field_kwargs: Optional[dict] = None,
    ):
        """
        Protection from execution of :func:`to_wtf_field` in form generation.

        :raises NotImplementedError: Field converter to WTForm Field not implemented.
        """
        raise NotImplementedError("Field converter to WTForm Field not implemented.")


class MultiPointField(WtfFieldMixin, fields.MultiPointField):
    """
    Extends :class:`mongoengine.fields.MultiPointField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    def to_wtf_field(
        self,
        *,
        model: Optional[Type] = None,
        field_kwargs: Optional[dict] = None,
    ):
        """
        Protection from execution of :func:`to_wtf_field` in form generation.

        :raises NotImplementedError: Field converter to WTForm Field not implemented.
        """
        raise NotImplementedError("Field converter to WTForm Field not implemented.")


class MultiPolygonField(WtfFieldMixin, fields.MultiPolygonField):
    """
    Extends :class:`mongoengine.fields.MultiPolygonField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    def to_wtf_field(
        self,
        *,
        model: Optional[Type] = None,
        field_kwargs: Optional[dict] = None,
    ):
        """
        Protection from execution of :func:`to_wtf_field` in form generation.

        :raises NotImplementedError: Field converter to WTForm Field not implemented.
        """
        raise NotImplementedError("Field converter to WTForm Field not implemented.")


class ObjectIdField(WtfFieldMixin, fields.ObjectIdField):
    """
    Extends :class:`mongoengine.fields.ObjectIdField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    DEFAULT_WTF_CHOICES_COERCE = ObjectId

    def to_wtf_field(
        self,
        *,
        model: Optional[Type] = None,
        field_kwargs: Optional[dict] = None,
    ):
        """
        Protection from execution of :func:`to_wtf_field` in form generation.

        :raises NotImplementedError: Field converter to WTForm Field not implemented.
        """
        raise NotImplementedError("Field converter to WTForm Field not implemented.")


class PointField(WtfFieldMixin, fields.PointField):
    """
    Extends :class:`mongoengine.fields.PointField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    def to_wtf_field(
        self,
        *,
        model: Optional[Type] = None,
        field_kwargs: Optional[dict] = None,
    ):
        """
        Protection from execution of :func:`to_wtf_field` in form generation.

        :raises NotImplementedError: Field converter to WTForm Field not implemented.
        """
        raise NotImplementedError("Field converter to WTForm Field not implemented.")


class PolygonField(WtfFieldMixin, fields.PolygonField):
    """
    Extends :class:`mongoengine.fields.PolygonField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    def to_wtf_field(
        self,
        *,
        model: Optional[Type] = None,
        field_kwargs: Optional[dict] = None,
    ):
        """
        Protection from execution of :func:`to_wtf_field` in form generation.

        :raises NotImplementedError: Field converter to WTForm Field not implemented.
        """
        raise NotImplementedError("Field converter to WTForm Field not implemented.")


class ReferenceField(WtfFieldMixin, fields.ReferenceField):
    """
    Extends :class:`mongoengine.fields.ReferenceField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    DEFAULT_WTF_FIELD = custom_fields.ModelSelectField if custom_fields else None

    def to_wtf_field(
        self,
        *,
        model: Optional[Type] = None,
        field_kwargs: Optional[dict] = None,
    ):
        """
        Protection from execution of :func:`to_wtf_field` in form generation.

        :raises NotImplementedError: Field converter to WTForm Field not implemented.
        """
        raise NotImplementedError("Field converter to WTForm Field not implemented.")


class SequenceField(WtfFieldMixin, fields.SequenceField):
    """
    Extends :class:`mongoengine.fields.SequenceField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    def to_wtf_field(
        self,
        *,
        model: Optional[Type] = None,
        field_kwargs: Optional[dict] = None,
    ):
        """
        Protection from execution of :func:`to_wtf_field` in form generation.

        :raises NotImplementedError: Field converter to WTForm Field not implemented.
        """
        raise NotImplementedError("Field converter to WTForm Field not implemented.")


class SortedListField(WtfFieldMixin, fields.SortedListField):
    """
    Extends :class:`mongoengine.fields.SortedListField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    DEFAULT_WTF_FIELD = wtf_fields.FieldList if wtf_fields else None

    def to_wtf_field(
        self,
        *,
        model: Optional[Type] = None,
        field_kwargs: Optional[dict] = None,
    ):
        """
        Protection from execution of :func:`to_wtf_field` in form generation.

        :raises NotImplementedError: Field converter to WTForm Field not implemented.
        """
        raise NotImplementedError("Field converter to WTForm Field not implemented.")


class StringField(WtfFieldMixin, fields.StringField):
    """
    Extends :class:`mongoengine.fields.StringField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.

    .. versionchanged:: 2.0.0
        Default form field output changed from :class:`.NoneStringField` to
        :class:`flask_mongoengine.wtf.fields.MongoTextAreaField`
    """

    DEFAULT_WTF_FIELD = custom_fields.MongoTextAreaField if custom_fields else None

    def __init__(
        self,
        *,
        password: bool = False,
        textarea: bool = False,
        validators: Optional[Union[List, Callable]] = None,
        filters: Optional[Union[List, Callable]] = None,
        wtf_field_class: Optional[Type] = None,
        wtf_filters: Optional[Union[List, Callable]] = None,
        wtf_validators: Optional[Union[List, Callable]] = None,
        wtf_choices_coerce: Optional[Callable] = None,
        wtf_options: Optional[dict] = None,
        **kwargs,
    ):
        """
        Extended :func:`__init__` method for mongoengine db field with WTForms options.

        :param password:
            DEPRECATED: Force to use :class:`~.MongoPasswordField` for field generation.
            In case of :attr:`password` and :attr:`wtf_field_class` both set, then
            :attr:`wtf_field_class` will be used.
        :param textarea:
            DEPRECATED: Force to use :class:`~.MongoTextAreaField` for field generation.
            In case of :attr:`textarea` and :attr:`wtf_field_class` both set, then
            :attr:`wtf_field_class` will be used.
        :param filters:     DEPRECATED: wtf form field filters.
        :param validators:  DEPRECATED: wtf form field validators.
        :param wtf_field_class: Any subclass of :class:`wtforms.forms.core.Field` that
            can be used for form field generation. Takes precedence over
            :attr:`DEFAULT_WTF_FIELD`  and :attr:`DEFAULT_WTF_CHOICES_FIELD`
        :param wtf_filters:     wtf form field filters.
        :param wtf_validators:  wtf form field validators.
        :param wtf_choices_coerce: Callable function to replace
            :attr:`DEFAULT_WTF_CHOICES_COERCE` for choices fields.
        :param wtf_options: Dictionary with WTForm Field settings.
            Applied last, takes precedence over any generated field options.
        :param kwargs: keyword arguments silently bypassed to normal mongoengine fields
        """
        if password:
            if textarea:
                raise ValueError("Password field cannot use TextAreaField class.")

            warnings.warn(
                (
                    "Passing 'password' keyword argument to field definition is "
                    "deprecated and will be removed in version 3.0.0. "
                    "Please use 'wtf_field_class' parameter to specify correct field "
                    "class. If both values set, 'wtf_field_class' is used."
                ),
                DeprecationWarning,
                stacklevel=2,
            )
            wtf_field_class = wtf_field_class or custom_fields.MongoPasswordField

        if textarea:
            warnings.warn(
                (
                    "Passing 'textarea' keyword argument to field definition is "
                    "deprecated and will be removed in version 3.0.0. "
                    "Please use 'wtf_field_class' parameter to specify correct field "
                    "class. If both values set, 'wtf_field_class' is used."
                ),
                DeprecationWarning,
                stacklevel=2,
            )
            wtf_field_class = wtf_field_class or custom_fields.MongoTextAreaField

        super().__init__(
            validators=validators,
            filters=filters,
            wtf_field_class=wtf_field_class,
            wtf_filters=wtf_filters,
            wtf_validators=wtf_validators,
            wtf_choices_coerce=wtf_choices_coerce,
            wtf_options=wtf_options,
            **kwargs,
        )

    @property
    def wtf_field_class(self) -> Type:
        """Parent class overwrite with support of class adjustment by field size."""
        if self._wtf_field_class:
            return self._wtf_field_class
        if self.max_length or self.min_length:
            return custom_fields.MongoStringField
        return super().wtf_field_class

    @property
    @wtf_required
    def wtf_generated_options(self) -> dict:
        """
        Extend form validators with :class:`wtforms.validators.Regexp` and
        :class:`wtforms.validators.Length`.
        """
        options = super().wtf_generated_options
        options = _setup_strings_common_validators(options, self)

        return options


class URLField(WtfFieldMixin, fields.URLField):
    """
    Extends :class:`mongoengine.fields.URLField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.

    .. versionchanged:: 2.0.0
        Default form field output changed from :class:`.NoneStringField` to
        :class:`~flask_mongoengine.wtf.fields.MongoURLField`

    .. versionchanged:: 2.0.0
        Now appends :class:`~wtforms.validators.Regexp` and use regexp provided to
        __init__ :attr:`url_regex`, instead of using non-configurable regexp from
        :class:`~wtforms.validators.URL`. This includes configuration conflicts, between
        modules.
    """

    DEFAULT_WTF_FIELD = custom_fields.MongoURLField if custom_fields else None

    @property
    @wtf_required
    def wtf_generated_options(self) -> dict:
        """Extend form validators with :class:`wtforms.validators.Regexp`"""
        options = super().wtf_generated_options
        options = _setup_strings_common_validators(options, self)
        options["validators"].insert(
            0, wtf_validators_.Regexp(regex=self.url_regex, message="Invalid URL.")
        )

        return options


class UUIDField(WtfFieldMixin, fields.UUIDField):
    """
    Extends :class:`mongoengine.fields.UUIDField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    def to_wtf_field(
        self,
        *,
        model: Optional[Type] = None,
        field_kwargs: Optional[dict] = None,
    ):
        """
        Protection from execution of :func:`to_wtf_field` in form generation.

        :raises NotImplementedError: Field converter to WTForm Field not implemented.
        """
        raise NotImplementedError("Field converter to WTForm Field not implemented.")

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
from typing import Callable, List, Optional, Union

from bson import ObjectId
from mongoengine import fields

try:
    from wtforms import fields as wtf_fields
    from wtforms import validators as wtf_validators

    from flask_mongoengine.wtf import fields as custom_fields
except ImportError:  # pragma: no cover
    custom_fields = None
    wtf_fields = None
    wtf_validators = None


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
    DEFAULT_WTF_CHOICES_FIELD_COERCE = str

    def __init__(
        self,
        *,
        validators: Optional[Union[List, Callable]] = None,
        filters: Optional[Union[List, Callable]] = None,
        wtf_filters: Optional[Union[List, Callable]] = None,
        wtf_validators: Optional[Union[List, Callable]] = None,
        **kwargs,
    ):
        """
        Extended :func:`__init__` method for mongoengine db field with WTForms options.

        :param filters:     DEPRECATED: wtf form field filters.
        :param validators:  DEPRECATED: wtf form field validators.
        :param wtf_filters:     wtf form field filters.
        :param wtf_validators:  wtf form field validators.
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

        # Some attributes that will be updated by parent methods
        self.required = False
        self.default = None
        self.name = ""

        super().__init__(**kwargs)

    @staticmethod
    def _ensure_callable_or_list(argument, msg_flag: str) -> Optional[List]:
        """
        Ensure submitted argument value is a callable object or valid list value.

        :param argument: Argument input to make verification on.
        :param msg_flag: Argument string name for error message.
        """
        if argument is None:
            return None

        if callable(argument):
            return [argument]
        elif not isinstance(argument, list):
            raise TypeError(f"Argument '{msg_flag}' must be a list value")

        return argument

    def to_wtf_field(self, model, field_kwargs):
        """
        Protection from execution of :func:`to_wtf_field` in form generation.

        :raises NotImplementedError: Field converter to WTForm Field not implemented.
        """
        raise NotImplementedError("Field converter to WTForm Field not implemented.")


class BinaryField(WtfFieldMixin, fields.BinaryField):
    """
    Extends :class:`mongoengine.fields.BinaryField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    DEFAULT_WTF_FIELD = custom_fields.BinaryField if custom_fields else None

    def to_wtf_field(self, model, field_kwargs):
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

    DEFAULT_WTF_FIELD = wtf_fields.BooleanField if wtf_fields else None
    DEFAULT_WTF_CHOICES_FIELD_COERCE = bool

    def to_wtf_field(self, model, field_kwargs):
        """
        Protection from execution of :func:`to_wtf_field` in form generation.

        :raises NotImplementedError: Field converter to WTForm Field not implemented.
        """
        raise NotImplementedError("Field converter to WTForm Field not implemented.")


class CachedReferenceField(WtfFieldMixin, fields.CachedReferenceField):
    """
    Extends :class:`mongoengine.fields.CachedReferenceField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    def to_wtf_field(self, model, field_kwargs):
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
    """

    def to_wtf_field(self, model, field_kwargs):
        """
        Protection from execution of :func:`to_wtf_field` in form generation.

        :raises NotImplementedError: Field converter to WTForm Field not implemented.
        """
        raise NotImplementedError("Field converter to WTForm Field not implemented.")


class DateField(WtfFieldMixin, fields.DateField):
    """
    Extends :class:`mongoengine.fields.DateField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    DEFAULT_WTF_FIELD = wtf_fields.DateField if wtf_fields else None

    def to_wtf_field(self, model, field_kwargs):
        """
        Protection from execution of :func:`to_wtf_field` in form generation.

        :raises NotImplementedError: Field converter to WTForm Field not implemented.
        """
        raise NotImplementedError("Field converter to WTForm Field not implemented.")


class DateTimeField(WtfFieldMixin, fields.DateTimeField):
    """
    Extends :class:`mongoengine.fields.DateTimeField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    DEFAULT_WTF_FIELD = wtf_fields.DateTimeField if wtf_fields else None

    def to_wtf_field(self, model, field_kwargs):
        """
        Protection from execution of :func:`to_wtf_field` in form generation.

        :raises NotImplementedError: Field converter to WTForm Field not implemented.
        """
        raise NotImplementedError("Field converter to WTForm Field not implemented.")


class DecimalField(WtfFieldMixin, fields.DecimalField):
    """
    Extends :class:`mongoengine.fields.DecimalField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    DEFAULT_WTF_FIELD = wtf_fields.DecimalField if wtf_fields else None
    DEFAULT_WTF_CHOICES_FIELD_COERCE = decimal.Decimal

    def to_wtf_field(self, model, field_kwargs):
        """
        Protection from execution of :func:`to_wtf_field` in form generation.

        :raises NotImplementedError: Field converter to WTForm Field not implemented.
        """
        raise NotImplementedError("Field converter to WTForm Field not implemented.")


class DictField(WtfFieldMixin, fields.DictField):
    """
    Extends :class:`mongoengine.fields.DictField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    DEFAULT_WTF_FIELD = custom_fields.DictField if custom_fields else None

    def to_wtf_field(self, model, field_kwargs):
        """
        Protection from execution of :func:`to_wtf_field` in form generation.

        :raises NotImplementedError: Field converter to WTForm Field not implemented.
        """
        raise NotImplementedError("Field converter to WTForm Field not implemented.")


class DynamicField(WtfFieldMixin, fields.DynamicField):
    """
    Extends :class:`mongoengine.fields.DynamicField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    def to_wtf_field(self, model, field_kwargs):
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
        Default field output changed from :class:`.NoneStringField` to
        :class:`wtforms.fields.EmailField`
    """

    DEFAULT_WTF_FIELD = wtf_fields.EmailField if wtf_fields else None

    def to_wtf_field(self, model, field_kwargs):
        """
        Protection from execution of :func:`to_wtf_field` in form generation.

        :raises NotImplementedError: Field converter to WTForm Field not implemented.
        """
        raise NotImplementedError("Field converter to WTForm Field not implemented.")


class EmbeddedDocumentField(WtfFieldMixin, fields.EmbeddedDocumentField):
    """
    Extends :class:`mongoengine.fields.EmbeddedDocumentField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    DEFAULT_WTF_FIELD = wtf_fields.FormField if wtf_fields else None

    def to_wtf_field(self, model, field_kwargs):
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

    def to_wtf_field(self, model, field_kwargs):
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

    def to_wtf_field(self, model, field_kwargs):
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

    def to_wtf_field(self, model, field_kwargs):
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
    """

    DEFAULT_WTF_FIELD = wtf_fields.FloatField if wtf_fields else None
    DEFAULT_WTF_CHOICES_FIELD_COERCE = float

    def to_wtf_field(self, model, field_kwargs):
        """
        Protection from execution of :func:`to_wtf_field` in form generation.

        :raises NotImplementedError: Field converter to WTForm Field not implemented.
        """
        raise NotImplementedError("Field converter to WTForm Field not implemented.")


class GenericEmbeddedDocumentField(WtfFieldMixin, fields.GenericEmbeddedDocumentField):
    """
    Extends :class:`mongoengine.fields.GenericEmbeddedDocumentField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    def to_wtf_field(self, model, field_kwargs):
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

    def to_wtf_field(self, model, field_kwargs):
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

    def to_wtf_field(self, model, field_kwargs):
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

    def to_wtf_field(self, model, field_kwargs):
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

    def to_wtf_field(self, model, field_kwargs):
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

    def to_wtf_field(self, model, field_kwargs):
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
    DEFAULT_WTF_CHOICES_FIELD_COERCE = int

    def to_wtf_field(self, model, field_kwargs):
        """
        Protection from execution of :func:`to_wtf_field` in form generation.

        :raises NotImplementedError: Field converter to WTForm Field not implemented.
        """
        raise NotImplementedError("Field converter to WTForm Field not implemented.")


class LazyReferenceField(WtfFieldMixin, fields.LazyReferenceField):
    """
    Extends :class:`mongoengine.fields.LazyReferenceField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    def to_wtf_field(self, model, field_kwargs):
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

    def to_wtf_field(self, model, field_kwargs):
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

    def to_wtf_field(self, model, field_kwargs):
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

    def to_wtf_field(self, model, field_kwargs):
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

    def to_wtf_field(self, model, field_kwargs):
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

    def to_wtf_field(self, model, field_kwargs):
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

    def to_wtf_field(self, model, field_kwargs):
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

    def to_wtf_field(self, model, field_kwargs):
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

    DEFAULT_WTF_CHOICES_FIELD_COERCE = ObjectId

    def to_wtf_field(self, model, field_kwargs):
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

    def to_wtf_field(self, model, field_kwargs):
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

    def to_wtf_field(self, model, field_kwargs):
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

    def to_wtf_field(self, model, field_kwargs):
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

    def to_wtf_field(self, model, field_kwargs):
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

    def to_wtf_field(self, model, field_kwargs):
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
    """

    DEFAULT_WTF_FIELD = wtf_fields.TextAreaField if wtf_fields else None

    def to_wtf_field(self, model, field_kwargs):
        """
        Protection from execution of :func:`to_wtf_field` in form generation.

        :raises NotImplementedError: Field converter to WTForm Field not implemented.
        """
        raise NotImplementedError("Field converter to WTForm Field not implemented.")


class URLField(WtfFieldMixin, fields.URLField):
    """
    Extends :class:`mongoengine.fields.URLField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    DEFAULT_WTF_FIELD = custom_fields.NoneStringField if custom_fields else None

    def to_wtf_field(self, model, field_kwargs):
        """
        Protection from execution of :func:`to_wtf_field` in form generation.

        :raises NotImplementedError: Field converter to WTForm Field not implemented.
        """
        raise NotImplementedError("Field converter to WTForm Field not implemented.")


class UUIDField(WtfFieldMixin, fields.UUIDField):
    """
    Extends :class:`mongoengine.fields.UUIDField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    All arguments should be passed as keyword arguments, to exclude unexpected behaviour.
    """

    def to_wtf_field(self, model, field_kwargs):
        """
        Protection from execution of :func:`to_wtf_field` in form generation.

        :raises NotImplementedError: Field converter to WTForm Field not implemented.
        """
        raise NotImplementedError("Field converter to WTForm Field not implemented.")

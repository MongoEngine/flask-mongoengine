"""Responsible for mongoengine fields extension, if WTFForms integration used."""
from typing import Callable, List, Optional, Union

try:
    from wtforms import fields as wtf_fields
    from wtforms import validators as wtf_validators
except ImportError:
    wtf_fields = None
    wtf_validators = None


from mongoengine import fields

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


class WtfFieldMixin:
    """
    Extension wrapper class for mongoengine BaseField.

    This enables flask-mongoengine  wtf to extend the
    number of field parameters, and settings on behalf
    of document model form generator for WTForm.

    :param validators:  wtf model form field validators.
    :param filters:     wtf model form field filters.
    :param kwargs: keyword arguments silently bypassed to normal mongoengine fields
    """

    def __init__(
        self,
        *,
        validators: Optional[Union[List, Callable]] = None,
        filters: Optional[Union[List, Callable]] = None,
        **kwargs,
    ):
        self.validators = self._ensure_callable_or_list(validators, "validators")
        self.filters = self._ensure_callable_or_list(filters, "filters")

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


class BinaryField(WtfFieldMixin, fields.BinaryField):
    """
    Extends :class:`mongoengine.fields.BinaryField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    """

    pass


class BooleanField(WtfFieldMixin, fields.BooleanField):
    """
    Extends :class:`mongoengine.fields.BooleanField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    """

    pass


class CachedReferenceField(WtfFieldMixin, fields.CachedReferenceField):
    """
    Extends :class:`mongoengine.fields.CachedReferenceField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    """

    pass


class ComplexDateTimeField(WtfFieldMixin, fields.ComplexDateTimeField):
    """
    Extends :class:`mongoengine.fields.ComplexDateTimeField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    """

    pass


class DateField(WtfFieldMixin, fields.DateField):
    """
    Extends :class:`mongoengine.fields.DateField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    """

    pass


class DateTimeField(WtfFieldMixin, fields.DateTimeField):
    """
    Extends :class:`mongoengine.fields.DateTimeField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    """

    pass


class DecimalField(WtfFieldMixin, fields.DecimalField):
    """
    Extends :class:`mongoengine.fields.DecimalField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    """

    pass


class DictField(WtfFieldMixin, fields.DictField):
    """
    Extends :class:`mongoengine.fields.DictField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    """

    pass


class DynamicField(WtfFieldMixin, fields.DynamicField):
    """
    Extends :class:`mongoengine.fields.DynamicField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    """

    pass


class EmailField(WtfFieldMixin, fields.EmailField):
    """
    Extends :class:`mongoengine.fields.EmailField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    """

    pass


class EmbeddedDocumentField(WtfFieldMixin, fields.EmbeddedDocumentField):
    """
    Extends :class:`mongoengine.fields.EmbeddedDocumentField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    """

    pass


class EmbeddedDocumentListField(WtfFieldMixin, fields.EmbeddedDocumentListField):
    """
    Extends :class:`mongoengine.fields.EmbeddedDocumentListField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    """

    pass


class EnumField(WtfFieldMixin, fields.EnumField):
    """
    Extends :class:`mongoengine.fields.EnumField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    """

    pass


class FileField(WtfFieldMixin, fields.FileField):
    """
    Extends :class:`mongoengine.fields.FileField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    """

    pass


class FloatField(WtfFieldMixin, fields.FloatField):
    """
    Extends :class:`mongoengine.fields.FloatField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    """

    pass


class GenericEmbeddedDocumentField(WtfFieldMixin, fields.GenericEmbeddedDocumentField):
    """
    Extends :class:`mongoengine.fields.GenericEmbeddedDocumentField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    """

    pass


class GenericLazyReferenceField(WtfFieldMixin, fields.GenericLazyReferenceField):
    """
    Extends :class:`mongoengine.fields.GenericLazyReferenceField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    """

    pass


class GenericReferenceField(WtfFieldMixin, fields.GenericReferenceField):
    """
    Extends :class:`mongoengine.fields.GenericReferenceField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    """

    pass


class GeoJsonBaseField(WtfFieldMixin, fields.GeoJsonBaseField):
    """
    Extends :class:`mongoengine.fields.GeoJsonBaseField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    """

    pass


class GeoPointField(WtfFieldMixin, fields.GeoPointField):
    """
    Extends :class:`mongoengine.fields.GeoPointField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    """

    pass


class ImageField(WtfFieldMixin, fields.ImageField):
    """
    Extends :class:`mongoengine.fields.ImageField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    """

    pass


class IntField(WtfFieldMixin, fields.IntField):
    """
    Extends :class:`mongoengine.fields.IntField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    """

    pass


class LazyReferenceField(WtfFieldMixin, fields.LazyReferenceField):
    """
    Extends :class:`mongoengine.fields.LazyReferenceField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    """

    pass


class LineStringField(WtfFieldMixin, fields.LineStringField):
    """
    Extends :class:`mongoengine.fields.LineStringField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    """

    pass


class ListField(WtfFieldMixin, fields.ListField):
    """
    Extends :class:`mongoengine.fields.ListField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    """

    pass


class LongField(WtfFieldMixin, fields.LongField):
    """
    Extends :class:`mongoengine.fields.LongField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    """

    pass


class MapField(WtfFieldMixin, fields.MapField):
    """
    Extends :class:`mongoengine.fields.MapField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    """

    pass


class MultiLineStringField(WtfFieldMixin, fields.MultiLineStringField):
    """
    Extends :class:`mongoengine.fields.MultiLineStringField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    """

    pass


class MultiPointField(WtfFieldMixin, fields.MultiPointField):
    """
    Extends :class:`mongoengine.fields.MultiPointField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    """

    pass


class MultiPolygonField(WtfFieldMixin, fields.MultiPolygonField):
    """
    Extends :class:`mongoengine.fields.MultiPolygonField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    """

    pass


class ObjectIdField(WtfFieldMixin, fields.ObjectIdField):
    """
    Extends :class:`mongoengine.fields.ObjectIdField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    """

    pass


class PointField(WtfFieldMixin, fields.PointField):
    """
    Extends :class:`mongoengine.fields.PointField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    """

    pass


class PolygonField(WtfFieldMixin, fields.PolygonField):
    """
    Extends :class:`mongoengine.fields.PolygonField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    """

    pass


class ReferenceField(WtfFieldMixin, fields.ReferenceField):
    """
    Extends :class:`mongoengine.fields.ReferenceField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    """

    pass


class SequenceField(WtfFieldMixin, fields.SequenceField):
    """
    Extends :class:`mongoengine.fields.SequenceField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    """

    pass


class SortedListField(WtfFieldMixin, fields.SortedListField):
    """
    Extends :class:`mongoengine.fields.SortedListField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    """

    pass


class StringField(WtfFieldMixin, fields.StringField):
    """
    Extends :class:`mongoengine.fields.StringField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    """

    pass


class URLField(WtfFieldMixin, fields.URLField):
    """
    Extends :class:`mongoengine.fields.URLField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    """

    pass


class UUIDField(WtfFieldMixin, fields.UUIDField):
    """
    Extends :class:`mongoengine.fields.UUIDField` with wtf required parameters.

    For full list of arguments and keyword arguments, look parent field docs.
    """

    pass

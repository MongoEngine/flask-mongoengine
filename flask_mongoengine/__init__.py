import mongoengine
from flask import Flask, abort, current_app
from mongoengine.errors import DoesNotExist
from mongoengine.queryset import QuerySet

from .connection import *
from .json import override_json_encoder
from .pagination import *
from .sessions import *
from .wtf import db_fields

VERSION = (1, 0, 0)


def get_version():
    """Return the VERSION as a string."""
    return ".".join(map(str, VERSION))


__version__ = get_version()


def current_mongoengine_instance():
    """Return a MongoEngine instance associated with current Flask app."""
    me = current_app.extensions.get("mongoengine", {})
    for k, v in me.items():
        if isinstance(k, MongoEngine):
            return k


class MongoEngine(object):
    """Main class used for initialization of Flask-MongoEngine."""

    def __init__(self, app=None, config=None):
        # Extended database fields
        self.BinaryField = db_fields.BinaryField
        self.BooleanField = db_fields.BooleanField
        self.CachedReferenceField = db_fields.CachedReferenceField
        self.ComplexDateTimeField = db_fields.ComplexDateTimeField
        self.DateField = db_fields.DateField
        self.DateTimeField = db_fields.DateTimeField
        self.DecimalField = db_fields.DecimalField
        self.DictField = db_fields.DictField
        self.DynamicField = db_fields.DynamicField
        self.EmailField = db_fields.EmailField
        self.EmbeddedDocumentField = db_fields.EmbeddedDocumentField
        self.EmbeddedDocumentListField = db_fields.EmbeddedDocumentListField
        self.EnumField = db_fields.EnumField
        self.FileField = db_fields.FileField
        self.FloatField = db_fields.FloatField
        self.GenericEmbeddedDocumentField = db_fields.GenericEmbeddedDocumentField
        self.GenericLazyReferenceField = db_fields.GenericLazyReferenceField
        self.GenericReferenceField = db_fields.GenericReferenceField
        self.GeoJsonBaseField = db_fields.GeoJsonBaseField
        self.GeoPointField = db_fields.GeoPointField
        self.ImageField = db_fields.ImageField
        self.IntField = db_fields.IntField
        self.LazyReferenceField = db_fields.LazyReferenceField
        self.LineStringField = db_fields.LineStringField
        self.ListField = db_fields.ListField
        self.LongField = db_fields.LongField
        self.MapField = db_fields.MapField
        self.MultiLineStringField = db_fields.MultiLineStringField
        self.MultiPointField = db_fields.MultiPointField
        self.MultiPolygonField = db_fields.MultiPolygonField
        self.ObjectIdField = db_fields.ObjectIdField
        self.PointField = db_fields.PointField
        self.PolygonField = db_fields.PolygonField
        self.ReferenceField = db_fields.ReferenceField
        self.SequenceField = db_fields.SequenceField
        self.SortedListField = db_fields.SortedListField
        self.StringField = db_fields.StringField
        self.URLField = db_fields.URLField
        self.UUIDField = db_fields.UUIDField

        # Flask related data
        self.app = None
        self.config = config

        # Extended documents classes
        self.Document = Document
        self.DynamicDocument = DynamicDocument

        if app is not None:
            self.init_app(app, config)

    def init_app(self, app, config=None):
        if not app or not isinstance(app, Flask):
            raise TypeError("Invalid Flask application instance")

        self.app = app

        app.extensions = getattr(app, "extensions", {})

        # Make documents JSON serializable
        override_json_encoder(app)

        if "mongoengine" not in app.extensions:
            app.extensions["mongoengine"] = {}

        if self in app.extensions["mongoengine"]:
            # Raise an exception if extension already initialized as
            # potentially new configuration would not be loaded.
            raise ValueError("Extension already initialized")

        if config:
            # Passed config have max priority, over init config.
            self.config = config

        if not self.config:
            # If no configs passed, use app.config.
            self.config = app.config

        # Obtain db connection(s)
        connections = create_connections(self.config)

        # Store objects in application instance so that multiple apps do not
        # end up accessing the same objects.
        s = {"app": app, "conn": connections}
        app.extensions["mongoengine"][self] = s

    @property
    def connection(self):
        """
        Return MongoDB connection(s) associated with this MongoEngine
        instance.
        """
        return current_app.extensions["mongoengine"][self]["conn"]

    def __getattr__(self, attr_name):
        """
        Mongoengine backward compatibility handler.

        Provide original :module:``mongoengine`` module methods/classes if they are not
        modified by us, and not mapped directly.
        """
        return getattr(mongoengine, attr_name)


class BaseQuerySet(QuerySet):
    """Extends :class:`~mongoengine.queryset.QuerySet` class with handly methods."""

    def _abort_404(self, _message_404):
        """Returns 404 error with message, if message provided.

        :param _message_404: Message for 404 comment
        """
        abort(404, _message_404) if _message_404 else abort(404)

    def get_or_404(self, *args, _message_404=None, **kwargs):
        """Get a document and raise a 404 Not Found error if it doesn't exist.

        :param _message_404: Message for 404 comment, not forwarded to
            :func:`~mongoengine.queryset.QuerySet.get`
        :param args: args list, silently forwarded to
            :func:`~mongoengine.queryset.QuerySet.get`
        :param kwargs: keywords arguments, silently forwarded to
            :func:`~mongoengine.queryset.QuerySet.get`
        """
        try:
            return self.get(*args, **kwargs)
        except DoesNotExist:
            self._abort_404(_message_404)

    def first_or_404(self, _message_404=None):
        """
        Same as :func:`~BaseQuerySet.get_or_404`, but uses
        :func:`~mongoengine.queryset.QuerySet.first`, not
        :func:`~mongoengine.queryset.QuerySet.get`.

        :param _message_404: Message for 404 comment, not forwarded to
            :func:`~mongoengine.queryset.QuerySet.get`
        """
        return self.first() or self._abort_404(_message_404)

    def paginate(self, page, per_page, **kwargs):
        """
        Paginate the QuerySet with a certain number of docs per page
        and return docs for a given page.
        """
        return Pagination(self, page, per_page)

    def paginate_field(self, field_name, doc_id, page, per_page, total=None):
        """
        Paginate items within a list field from one document in the
        QuerySet.
        """
        # TODO this doesn't sound useful at all - remove in next release?
        item = self.get(id=doc_id)
        count = getattr(item, field_name + "_count", "")
        total = total or count or len(getattr(item, field_name))
        return ListFieldPagination(
            self, doc_id, field_name, page, per_page, total=total
        )


class Document(mongoengine.Document):
    """Abstract document with extra helpers in the queryset class"""

    meta = {"abstract": True, "queryset_class": BaseQuerySet}

    def paginate_field(self, field_name, page, per_page, total=None):
        """Paginate items within a list field."""
        # TODO this doesn't sound useful at all - remove in next release?
        count = getattr(self, field_name + "_count", "")
        total = total or count or len(getattr(self, field_name))
        return ListFieldPagination(
            self.__class__.objects, self.pk, field_name, page, per_page, total=total
        )


class DynamicDocument(mongoengine.DynamicDocument):
    """Abstract Dynamic document with extra helpers in the queryset class"""

    meta = {"abstract": True, "queryset_class": BaseQuerySet}

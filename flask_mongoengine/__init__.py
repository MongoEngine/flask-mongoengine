import warnings

import mongoengine
from flask import Flask, current_app

from flask_mongoengine import db_fields, documents
from flask_mongoengine.connection import *
from flask_mongoengine.json import override_json_encoder
from flask_mongoengine.pagination import *
from flask_mongoengine.sessions import *


def current_mongoengine_instance():
    """Return a MongoEngine instance associated with current Flask app."""
    me = current_app.extensions.get("mongoengine", {})
    for k, v in me.items():
        if isinstance(k, MongoEngine):
            return k


class MongoEngine:
    """Main class used for initialization of Flask-MongoEngine."""

    def __init__(self, app=None, config=None):
        if config is not None:
            warnings.warn(
                (
                    "Passing flat configuration is deprecated. Please check "
                    "http://docs.mongoengine.org/projects/flask-mongoengine/flask_config.html "
                    "for more info."
                ),
                DeprecationWarning,
                stacklevel=2,
            )
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
        self.Document = documents.Document
        self.DynamicDocument = documents.DynamicDocument

        if app is not None:
            self.init_app(app, config)

    def init_app(self, app, config=None):
        if not app or not isinstance(app, Flask):
            raise TypeError("Invalid Flask application instance")

        if config is not None:
            warnings.warn(
                (
                    "Passing flat configuration is deprecated. Please check "
                    "http://docs.mongoengine.org/projects/flask-mongoengine/flask_config.html "
                    "for more info."
                ),
                DeprecationWarning,
                stacklevel=2,
            )
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
    def connection(self) -> dict:
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

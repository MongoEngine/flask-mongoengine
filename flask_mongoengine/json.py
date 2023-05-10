"""Flask application JSON extension functions."""
from functools import lru_cache

from bson import DBRef, ObjectId, json_util
from mongoengine.base import BaseDocument
from mongoengine.queryset import QuerySet
from pymongo.command_cursor import CommandCursor


@lru_cache(maxsize=1)
def use_json_provider() -> bool:
    """Split Flask before 2.2.0 and after, to use/not use JSON provider approach."""
    from flask import __version__

    version = list(__version__.split("."))
    return int(version[0]) > 2 or (int(version[0]) == 2 and int(version[1]) > 1)


# noinspection PyProtectedMember
def _convert_mongo_objects(obj):
    """Convert objects, related to Mongo database to JSON."""
    converted = None
    if isinstance(obj, BaseDocument):
        converted = json_util._json_convert(obj.to_mongo())
    elif isinstance(obj, QuerySet):
        converted = json_util._json_convert(obj.as_pymongo())
    elif isinstance(obj, CommandCursor):
        converted = json_util._json_convert(obj)
    elif isinstance(obj, DBRef):
        converted = obj.id
    elif isinstance(obj, ObjectId):
        converted = obj.__str__()
    return converted


def _make_encoder(superclass):
    """Extend Flask JSON Encoder 'default' method with support of Mongo objects."""
    import warnings

    warnings.warn(
        (
            "JSONEncoder/JSONDecoder are deprecated in Flask 2.2 and will be removed "
            "in Flask 2.3."
        ),
        DeprecationWarning,
        stacklevel=2,
    )

    class MongoEngineJSONEncoder(superclass):
        """
        A JSONEncoder which provides serialization of MongoEngine
        documents and queryset objects.
        """

        def default(self, obj):
            """Extend JSONEncoder default method, with Mongo objects."""
            if isinstance(
                obj,
                (BaseDocument, QuerySet, CommandCursor, DBRef, ObjectId),
            ):
                return _convert_mongo_objects(obj)
            return super().default(obj)

    return MongoEngineJSONEncoder


def _update_json_provider(superclass):
    """Extend Flask Provider 'default' static method with support of Mongo objects."""

    class MongoEngineJSONProvider(superclass):
        """A JSON Provider update for Flask 2.2.0+"""

        @staticmethod
        def default(obj):
            """Extend JSONProvider default static method, with Mongo objects."""
            if isinstance(
                obj,
                (BaseDocument, QuerySet, CommandCursor, DBRef, ObjectId),
            ):
                return _convert_mongo_objects(obj)
            return superclass.default(obj)

    return MongoEngineJSONProvider


# Compatibility code for Flask 2.2.0+ support
MongoEngineJSONEncoder = None
MongoEngineJSONProvider = None

if use_json_provider():
    from flask.json.provider import DefaultJSONProvider

    MongoEngineJSONProvider = _update_json_provider(DefaultJSONProvider)
else:
    from flask.json import JSONEncoder

    MongoEngineJSONEncoder = _make_encoder(JSONEncoder)
# End of compatibility code


def override_json_encoder(app):
    """
    A function to dynamically create a new MongoEngineJSONEncoder class
    based upon a custom base class.
    This function allows us to combine MongoEngine serialization with
    any changes to Flask's JSONEncoder which a user may have made
    prior to calling init_app.

    NOTE: This does not cover situations where users override
    an instance's json_encoder after calling init_app.
    """

    if use_json_provider():
        app.json_provider_class = _update_json_provider(app.json_provider_class)
        app.json = app.json_provider_class(app)
    else:
        app.json_encoder = _make_encoder(app.json_encoder)

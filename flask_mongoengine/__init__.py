# -*- coding: utf-8 -*-
from __future__ import absolute_import

from flask import abort, current_app

import mongoengine
import mongoengine.connection
from mongoengine.connection import DEFAULT_CONNECTION_NAME

from mongoengine.queryset import MultipleObjectsReturned, DoesNotExist, QuerySet
from mongoengine.base import ValidationError

from pymongo import uri_parser

from .sessions import *
from .pagination import *
from .json import overide_json_encoder


# Dictionary to hold connection settings until `get_db` is executed. This
# allows creation of lazy connection objects.
pending_lazy_connections = {}


def _include_mongoengine(obj):
    for module in mongoengine, mongoengine.fields:
        for key in module.__all__:
            if not hasattr(obj, key):
                setattr(obj, key, getattr(module, key))


def _create_connection(conn_settings, lazy=False):

    # Handle multiple connections recursively
    if isinstance(conn_settings, list):
        connections = {}
        for conn in conn_settings:
            connections[conn.get('alias')] = _create_connection(conn)
        return connections

    conn = dict([(k.lower(), v) for k, v in conn_settings.items() if v])

    if 'replicaset' in conn:
        conn['replicaSet'] = conn.pop('replicaset')

    # Handle uri style connections
    if "://" in conn.get('host', ''):
        uri_dict = uri_parser.parse_uri(conn_settings['host'])
        conn['db'] = uri_dict['database']

    if lazy:
        pending_lazy_connections[conn.get('alias')] = conn
    else:
        return mongoengine.connect(conn.pop('db', 'test'), **conn)


def get_db(db_alias):
    """Gets db after ensuring lazy connection is connected."""
    if db_alias in pending_lazy_connections:
        conn = pending_lazy_connections.get(db_alias)
        mongoengine.connect(conn.pop('db', 'test'), **conn)
    return mongoengine.connection.get_db(db_alias)


class MongoEngine(object):

    def __init__(self, app=None, config=None):

        _include_mongoengine(self)

        self.Document = Document
        self.DynamicDocument = DynamicDocument

        if app is not None:
            self.init_app(app, config)

    def init_app(self, app, config=None):

        app.extensions = getattr(app, 'extensions', {})

        # Make documents JSON serializable
        overide_json_encoder(app)

        if not 'mongoengine' in app.extensions:
            app.extensions['mongoengine'] = {}

        if self in app.extensions['mongoengine']:
            # Raise an exception if extension already initialized as
            # potentially new configuration would not be loaded.
            raise Exception('Extension already initialized')

        if not config:
            # If not passed a config then we read the connection settings
            # from the app config.
            config = app.config

        if 'MONGODB_SETTINGS' in config:
            # Connection settings provided as a dictionary.
            settings = config['MONGODB_SETTINGS']
        else:
            # Connection settings provided in standard format.
            settings = {'alias': config.get('MONGODB_ALIAS', None),
                        'db': config.get('MONGODB_DB', None),
                        'host': config.get('MONGODB_HOST', None),
                        'password': config.get('MONGODB_PASSWORD', None),
                        'port': config.get('MONGODB_PORT', None),
                        'username': config.get('MONGODB_USERNAME', None)}

        # If the alias isn't set then use the default connection name,
        if not settings.get('alias'):
            settings['alias'] = DEFAULT_CONNECTION_NAME

        # Store objects in application instance so that multiple apps do
        # not end up accessing the same objects.
        app.extensions['mongoengine'][self] = {'app': app,
                                               'settings': settings}

        # Creating a lazy connection requires that your documents inherit from
        # the Document class defined in this extension. Otherwise mongoengine
        # will not have an initialized connection on first attempt to access
        # data.
        lazy = bool(config.get('MONGODB_LAZY_CONNECTION', False))
        _create_connection(settings, lazy=lazy)


class BaseQuerySet(QuerySet):
    """
    A base queryset with handy extras
    """

    def get_or_404(self, *args, **kwargs):
        try:
            return self.get(*args, **kwargs)
        except (MultipleObjectsReturned, DoesNotExist, ValidationError):
            abort(404)

    def first_or_404(self):

        obj = self.first()
        if obj is None:
            abort(404)

        return obj

    def paginate(self, page, per_page, error_out=True):
        return Pagination(self, page, per_page)

    def paginate_field(self, field_name, doc_id, page, per_page,
                       total=None):
        item = self.get(id=doc_id)
        count = getattr(item, field_name + "_count", '')
        total = total or count or len(getattr(item, field_name))
        return ListFieldPagination(self, doc_id, field_name, page, per_page,
                                   total=total)


class Document(mongoengine.Document):
    """Abstract document with extra helpers in the queryset class"""

    meta = {'abstract': True,
            'queryset_class': BaseQuerySet}

    def paginate_field(self, field_name, page, per_page, total=None):
        count = getattr(self, field_name + "_count", '')
        total = total or count or len(getattr(self, field_name))
        return ListFieldPagination(self.__class__.objects, self.pk, field_name,
                                   page, per_page, total=total)

    @classmethod
    def _get_db(cls):
        """Override so we can establish connections inside flask-mongoengine"""
        return get_db(cls._meta.get("db_alias", DEFAULT_CONNECTION_NAME))


class DynamicDocument(mongoengine.DynamicDocument):
    """Abstract Dynamic document with extra helpers in the queryset class"""

    meta = {'abstract': True,
            'queryset_class': BaseQuerySet}

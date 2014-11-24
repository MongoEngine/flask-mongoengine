# -*- coding: utf-8 -*-
from __future__ import absolute_import

from flask import abort, current_app

import mongoengine

from mongoengine.queryset import MultipleObjectsReturned, DoesNotExist, QuerySet
from mongoengine.base import ValidationError

from pymongo import uri_parser

from .sessions import *
from .pagination import *
from .json import overide_json_encoder


def _include_mongoengine(obj):
    for module in mongoengine, mongoengine.fields:
        for key in module.__all__:
            if not hasattr(obj, key):
                setattr(obj, key, getattr(module, key))


def _create_connection(conn_settings):

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

    return mongoengine.connect(conn.pop('db', 'test'), **conn)


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

        if config:
            # If passed an explicit config then we must make sure to ignore
            # anything set in the application config.
            connection = _create_connection(config)
        else:
            # Set default config
            config = {}
            config.setdefault('db', app.config.get('MONGODB_DB', None))
            config.setdefault('host', app.config.get('MONGODB_HOST', None))
            config.setdefault('port', app.config.get('MONGODB_PORT', None))
            config.setdefault('username',
                                app.config.get('MONGODB_USERNAME', None))
            config.setdefault('password',
                                app.config.get('MONGODB_PASSWORD', None))

            # Before using default config we check for MONGODB_SETTINGS
            if 'MONGODB_SETTINGS' in app.config:
                connection = _create_connection(app.config['MONGODB_SETTINGS'])
            else:
                connection = _create_connection(config)

        # Store objects in application instance so that multiple apps do
        # not end up accessing the same objects.
        app.extensions['mongoengine'][self] = {'app': app,
                                               'conn': connection}

    @property
    def connection(self):
        return current_app.extensions['mongoengine'][self]['conn']


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


class DynamicDocument(mongoengine.DynamicDocument):
    """Abstract Dynamic document with extra helpers in the queryset class"""

    meta = {'abstract': True,
            'queryset_class': BaseQuerySet}

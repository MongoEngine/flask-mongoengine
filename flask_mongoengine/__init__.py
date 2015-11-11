# -*- coding: utf-8 -*-
from __future__ import absolute_import
import inspect

from flask import abort, current_app

import mongoengine

if mongoengine.__version__ == '0.7.10':
    from mongoengine.base import BaseField
else:
    from mongoengine.base.fields import BaseField


from mongoengine.queryset import MultipleObjectsReturned, DoesNotExist, QuerySet
from mongoengine.base import ValidationError

from pymongo import uri_parser

from .sessions import *
from .pagination import *
from .metadata import *
from .json import overide_json_encoder
from .wtf import WtfBaseField

def _patch_base_field(object, name):
    """
    If the object submitted has a class whose base class is
    mongoengine.base.fields.BaseField, then monkey patch to
    replace it with flask_mongoengine.wtf.WtfBaseField.

    @note:  WtfBaseField is an instance of BaseField - but
            gives us the flexibility to extend field parameters
            and settings required of WTForm via model form generator.

    @see: flask_mongoengine.wtf.base.WtfBaseField.
    @see: model_form in flask_mongoengine.wtf.orm

    @param object:  The object whose footprint to locate the class.
    @param name:    Name of the class to locate.

    """
    # locate class
    cls = getattr(object, name)
    if not inspect.isclass(cls):
        return

    # fetch class base classes
    cls_bases = list(cls.__bases__)

    # replace BaseField with WtfBaseField
    for index, base in enumerate(cls_bases):
        if base == BaseField:
            cls_bases[index] = WtfBaseField
            cls.__bases__ = tuple(cls_bases)
            break

    # re-assign class back to
    # object footprint
    delattr(object, name)
    setattr(object, name, cls)


def _include_mongoengine(obj):
    for module in mongoengine, mongoengine.fields:
        for key in module.__all__:
            if not hasattr(obj, key):
                setattr(obj, key, getattr(module, key))

                # patch BaseField if available
                _patch_base_field(obj, key)


def _create_connection(conn_settings):

    # Handle multiple connections recursively
    if isinstance(conn_settings, list):
        connections = {}
        for conn in conn_settings:
            connections[conn.get('alias')] = _create_connection(conn)
        return connections

    # Ugly dict comprehention in order to support python 2.6
    conn = dict((k.lower(), v) for k, v in conn_settings.items() if v is not None)

    if 'replicaset' in conn:
        conn['replicaSet'] = conn.pop('replicaset')

    # Handle uri style connections
    if "://" in conn.get('host', ''):
        uri_dict = uri_parser.parse_uri(conn['host'])
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

        if not config:
            # If not passed a config then we read the connection settings
            # from the app config.
            config = app.config

        if 'MONGODB_SETTINGS' in config:
            # Connection settings provided as a dictionary.
            connection = _create_connection(config['MONGODB_SETTINGS'])
        else:
            # Connection settings provided in standard format.
            settings = {'alias': config.get('MONGODB_ALIAS', None),
                        'db': config.get('MONGODB_DB', None),
                        'host': config.get('MONGODB_HOST', None),
                        'password': config.get('MONGODB_PASSWORD', None),
                        'port': config.get('MONGODB_PORT', None),
                        'username': config.get('MONGODB_USERNAME', None)}
            connection = _create_connection(settings)

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

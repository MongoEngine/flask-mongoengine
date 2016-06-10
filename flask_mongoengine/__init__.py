# -*- coding: utf-8 -*-
from __future__ import absolute_import
import mongoengine, inspect

from flask import abort, current_app
from mongoengine.base.fields import BaseField
from mongoengine.queryset import (MultipleObjectsReturned,
    DoesNotExist, QuerySet)

from mongoengine.base import ValidationError
from pymongo import uri_parser
from .sessions import *
from .pagination import *
from .metadata import *
from .json import override_json_encoder
from .wtf import WtfBaseField
from .connection import *
import flask_mongoengine

def redirect_connection_calls(cls):
    """
    Redirect mongonengine.connection
    calls via flask_mongoengine.connection
    """

    # Proxy all 'mongoengine.connection'
    # specific attr via 'flask_mongoengine'
    connection_methods = {
        'get_db' : get_db,
        'DEFAULT_CONNECTION_NAME' : DEFAULT_CONNECTION_NAME,
        'get_connection' : get_connection
    }

    cls_module = inspect.getmodule(cls)
    if cls_module != mongoengine.connection:
        for attr in inspect.getmembers(cls_module):
            n = attr[0]
            if connection_methods.get(n, None):
                setattr(cls_module, n, connection_methods.get(n, None))

def _patch_base_field(obj, name):
    """
    If the object submitted has a class whose base class is
    mongoengine.base.fields.BaseField, then monkey patch to
    replace it with flask_mongoengine.wtf.WtfBaseField.

    @note:  WtfBaseField is an instance of BaseField - but
            gives us the flexibility to extend field parameters
            and settings required of WTForm via model form generator.

    @see: flask_mongoengine.wtf.base.WtfBaseField.
    @see: model_form in flask_mongoengine.wtf.orm

    @param obj:     The object whose footprint to locate the class.
    @param name:    Name of the class to locate.
    """

    # locate class
    cls = getattr(obj, name)
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
    delattr(obj, name)
    setattr(obj, name, cls)
    redirect_connection_calls(cls)

def _include_mongoengine(obj):
    for module in mongoengine, mongoengine.fields:
        for key in module.__all__:
            if not hasattr(obj, key):
                setattr(obj, key, getattr(module, key))

                # patch BaseField if available
                _patch_base_field(obj, key)

def current_mongoengine_instance():
    """
    Obtain instance of MongoEngine in the
    current working app instance.
    """
    me = current_app.extensions.get('mongoengine', None)
    if current_app and me:
        instance_dict = me.items()\
            if (sys.version_info >= (3, 0)) else me.iteritems()
        for k, v in instance_dict:
            if isinstance(k, MongoEngine):
                return k
    return None

class MongoEngine(object):

    def __init__(self, app=None, config=None):
        _include_mongoengine(self)

        self.Document = Document
        self.DynamicDocument = DynamicDocument

        if app is not None:
            self.init_app(app, config)

    def init_app(self, app, config=None):
        from flask import Flask
        if not app or not isinstance(app, Flask):
            raise Exception('Invalid Flask application instance')

        app.extensions = getattr(app, 'extensions', {})

        # Make documents JSON serializable
        override_json_encoder(app)

        if not 'mongoengine' in app.extensions:
            app.extensions['mongoengine'] = {}

        if self in app.extensions['mongoengine']:
            # Raise an exception if extension already initialized as
            # potentially new configuration would not be loaded.
            raise Exception('Extension already initialized')

        if not config:
            # If not passed a config then we
            # read the connection settings from
            # the app config.
            config = app.config

        # Obtain db connection
        connection = create_connection(config, app)

        # Store objects in application instance
        # so that multiple apps do not end up
        # accessing the same objects.
        s = {'app': app, 'conn': connection}
        app.extensions['mongoengine'][self] = s

    def disconnect(self):
        conn_settings = fetch_connection_settings(current_app.config)
        if isinstance(conn_settings, list):
            for setting in conn_settings:
                alias = setting.get('alias', DEFAULT_CONNECTION_NAME)
                disconnect(alias, setting.get('preserve_temp_db', False))
        else:
            alias = conn_settings.get('alias', DEFAULT_CONNECTION_NAME)
            disconnect(alias, conn_settings.get('preserve_temp_db', False))
        return True

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

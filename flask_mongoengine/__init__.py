# -*- coding: utf-8 -*-
from __future__ import absolute_import

from flask import abort

import mongoengine

from mongoengine.queryset import MultipleObjectsReturned, DoesNotExist, QuerySet
from mongoengine.base import ValidationError

from .sessions import *
from .pagination import *
from .json import overide_json_encoder


def _include_mongoengine(obj):
    for module in mongoengine, mongoengine.fields:
        for key in module.__all__:
            if not hasattr(obj, key):
                setattr(obj, key, getattr(module, key))


class MongoEngine(object):

    def __init__(self, app=None):

        _include_mongoengine(self)

        self.Document = Document
        self.DynamicDocument = DynamicDocument

        if app is not None:
            self.init_app(app)

    def init_app(self, app):

        conn_settings = app.config.get('MONGODB_SETTINGS', None)

        if not conn_settings:
            conn_settings = {
                'db': app.config.get('MONGODB_DB', None),
                'username': app.config.get('MONGODB_USERNAME', None),
                'password': app.config.get('MONGODB_PASSWORD', None),
                'host': app.config.get('MONGODB_HOST', None),
                'port': int(app.config.get('MONGODB_PORT', 0)) or None
            }

        if isinstance(conn_settings, list):
            self.connection = {}
            for conn in conn_settings:
                conn = dict([(k.lower(), v) for k, v in conn.items() if v])

                if 'replicaset' in conn:
                    conn['replicaSet'] = conn['replicaset']
                    del conn['replicaset']

                self.connection[conn.get('alias')] = mongoengine.connect(**conn)

        else:
            conn_settings = dict([(k.lower(), v) for k, v in conn_settings.items() if v])

            if 'replicaset' in conn_settings:
                conn_settings['replicaSet'] = conn_settings['replicaset']
                del conn_settings['replicaset']

            self.connection = mongoengine.connect(**conn_settings)

        app.extensions = getattr(app, 'extensions', {})
        app.extensions['mongoengine'] = self
        self.app = app
        overide_json_encoder(app)


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

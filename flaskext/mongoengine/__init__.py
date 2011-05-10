# -*- coding: utf-8 -*-
from __future__ import absolute_import

import math

import mongoengine

from mongoengine.queryset import MultipleObjectsReturned, DoesNotExist
from mongoengine.queryset import QuerySet as BaseQuerySet
from mongoengine import ValidationError

from flask import abort


def _include_mongoengine(obj):
    for module in mongoengine, mongoengine.fields:
        for key in module.__all__:
            if not hasattr(obj, key):
                setattr(obj, key, getattr(module, key))


class MongoEngine(object):

    def __init__(self, app=None):

        _include_mongoengine(self)

        self.QuerySet = QuerySet
        self.BaseQuerySet = BaseQuerySet

        if app is not None:
            self.init_app(app)

    def init_app(self, app):

        db = app.config['MONGODB_DB']
        username = app.config.get('MONGODB_USERNAME', None)
        password = app.config.get('MONGODB_PASSWORD', None)

        # more settings e.g. port etc needed

        self.connection = mongoengine.connect(
            db=db, username=username, password=password)


class QuerySet(BaseQuerySet):

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

        if error_out and page < 1:
            abort(404)

        offset = (page - 1) * per_page
        items = self[offset:per_page]

        if not items and page != 1 and error_out:
            abort(404)

        return Pagination(self, page, per_page, self.count(), items)


class Pagination(object):

    def __init__(self, queryset, page, per_page, total, items):

        self.queryset = queryset
        self.page = page
        self.per_page = per_page
        self.total = total
        self.items = items

    @property
    def pages(self):
        """The total number of pages"""
        return int(math.ceil(self.total / float(self.per_page)))

    def prev(self, error_out=False):
        """Returns a :class:`Pagination` object for the previous page."""
        assert self.queryset is not None, 'a query object is required ' \
                                       'for this method to work'
        return self.queryset.paginate(self.page - 1, self.per_page, error_out)

    @property
    def prev_num(self):
        """Number of the previous page."""
        return self.page - 1

    @property
    def has_prev(self):
        """True if a previous page exists"""
        return self.page > 1

    def next(self, error_out=False):
        """Returns a :class:`Pagination` object for the next page."""
        assert self.queryset is not None, 'a query object is required ' \
                                       'for this method to work'
        return self.queryset.paginate(self.page + 1, self.per_page, error_out)

    @property
    def has_next(self):
        """True if a next page exists."""
        return self.page < self.pages

    @property
    def next_num(self):
        """Number of the next page"""
        return self.page + 1

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        """Iterates over the page numbers in the pagination.  The four
        parameters control the thresholds how many numbers should be produced
        from the sides.  Skipped page numbers are represented as `None`.
        This is how you could render such a pagination in the templates:

        .. sourcecode:: html+jinja

            {% macro render_pagination(pagination, endpoint) %}
              <div class=pagination>
              {%- for page in pagination.iter_pages() %}
                {% if page %}
                  {% if page != pagination.page %}
                    <a href="{{ url_for(endpoint, page=page) }}">{{ page }}</a>
                  {% else %}
                    <strong>{{ page }}</strong>
                  {% endif %}
                {% else %}
                  <span class=ellipsis>…</span>
                {% endif %}
              {%- endfor %}
              </div>
            {% endmacro %}
        """
        last = 0
        for num in xrange(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and
                num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num

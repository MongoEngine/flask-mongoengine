"""Module responsible for custom pagination."""

from flask import abort

from flask_mongoengine.pagination.basic_pagination import Pagination


class ListFieldPagination(Pagination):
    def __init__(self, queryset, doc_id, field_name, page, per_page, total=None):
        """Allows an array within a document to be paginated.

        Queryset must contain the document which has the array we're
        paginating, and doc_id should be it's _id.
        Field name is the name of the array we're paginating.
        Page and per_page work just like in Pagination.
        Total is an argument because it can be computed more efficiently
        elsewhere, but we still use array.length as a fallback.
        """
        if page < 1:
            abort(404)

        self.page = page
        self.per_page = per_page

        self.queryset = queryset
        self.doc_id = doc_id
        self.field_name = field_name

        start_index = (page - 1) * per_page

        field_attrs = {field_name: {"$slice": [start_index, per_page]}}

        qs = queryset(pk=doc_id)
        self.items = getattr(qs.fields(**field_attrs).first(), field_name)
        self.total = total or len(
            getattr(qs.fields(**{field_name: 1}).first(), field_name)
        )

        if not self.items and page != 1:
            abort(404)

    def prev(self, error_out=False):
        """Returns a :class:`Pagination` object for the previous page."""
        assert (
            self.items is not None
        ), "a query object is required for this method to work"
        return self.__class__(
            self.queryset,
            self.doc_id,
            self.field_name,
            self.page - 1,
            self.per_page,
            self.total,
        )

    def next(self, error_out=False):
        """Returns a :class:`Pagination` object for the next page."""
        assert (
            self.items is not None
        ), "a query object is required for this method to work"
        return self.__class__(
            self.queryset,
            self.doc_id,
            self.field_name,
            self.page + 1,
            self.per_page,
            self.total,
        )

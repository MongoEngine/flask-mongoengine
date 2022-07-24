"""Extended version of :mod:`mongoengine.document`."""
import mongoengine
from flask import abort
from mongoengine.errors import DoesNotExist
from mongoengine.queryset import QuerySet

from flask_mongoengine.pagination import ListFieldPagination, Pagination


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
        count = getattr(item, f"{field_name}_count", "")
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
        count = getattr(self, f"{field_name}_count", "")
        total = total or count or len(getattr(self, field_name))
        return ListFieldPagination(
            self.__class__.objects, self.pk, field_name, page, per_page, total=total
        )


class DynamicDocument(mongoengine.DynamicDocument):
    """Abstract Dynamic document with extra helpers in the queryset class"""

    meta = {"abstract": True, "queryset_class": BaseQuerySet}

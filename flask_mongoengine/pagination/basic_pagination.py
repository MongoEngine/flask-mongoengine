import math

from flask import abort
from mongoengine.queryset import QuerySet

from flask_mongoengine.pagination.abc_pagination import ABCPagination


class Pagination(ABCPagination):
    def __init__(
        self,
        iterable,
        page: int,
        per_page: int,
        max_depth: int = None,
        first_page_index: int = 1,
    ):
        """
        :param iterable: iterable object .
        :param page: Required page number start from 1.
        :param per_page: Required number of documents per page.
        :param max_depth: Option for limit number of dereference documents.
        :param first_page_index: Option for change first page index.
        """

        if page < first_page_index:
            abort(404, "Invalid page number.")

        self.iterable = iterable
        self.page = page
        self.per_page = per_page
        self.first_page_index = first_page_index

        if isinstance(self.iterable, QuerySet):
            self.total = iterable.count()
            self.items = self.iterable.skip(
                self.per_page * (self.page - self.first_page_index)
            ).limit(self.per_page)
            if max_depth is not None:
                self.items = self.items.select_related(max_depth)
        else:
            start_index = (page - self.first_page_index) * per_page
            end_index = start_index + per_page

            self.total = len(iterable)
            self.items = iterable[start_index : min(end_index, self.total)]
        if not self.items and page != self.first_page_index:
            abort(404, "Invalid page number.")

    @property
    def pages(self) -> int:
        """The total number of pages"""
        return int(math.ceil(self.total / float(self.per_page)))

    def prev(self, error_out=False):
        """Returns a :class:`Pagination` object for the previous page."""
        assert (
            self.iterable is not None
        ), "an object is required for this method to work"
        iterable = self.iterable
        if isinstance(iterable, QuerySet):
            iterable._skip = None
            iterable._limit = None
        return self.__class__(
            iterable,
            page=self.page - 1,
            per_page=self.per_page,
            first_page_index=self.first_page_index,
        )

    @property
    def prev_num(self) -> int:
        """Number of the previous page."""
        return self.page - 1

    @property
    def has_prev(self) -> bool:
        """True if a previous page exists"""
        return self.page > self.first_page_index

    def next(self, error_out=False):
        """Returns a :class:`Pagination` object for the next page."""
        assert (
            self.iterable is not None
        ), "an object is required for this method to work"
        iterable = self.iterable
        if isinstance(iterable, QuerySet):
            iterable._skip = None
            iterable._limit = None
        return self.__class__(
            iterable,
            page=self.page + 1,
            per_page=self.per_page,
            first_page_index=self.first_page_index,
        )

    @property
    def has_next(self) -> bool:
        """True if a next page exists."""
        return self.page < self.last_page_index

    @property
    def last_page_index(self) -> int:
        """True if a next page exists."""
        return self.pages - 1 + self.first_page_index

    @property
    def next_num(self) -> int:
        """Number of the next page"""
        return self.page + 1

    def iter_pages(
        self, left_edge=2, left_current=2, right_current=5, right_edge=2
    ):  # TODO: documentation!!!
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

        last = -1 + self.first_page_index
        for num in range(self.first_page_index, self.pages + self.first_page_index):
            if (
                num <= left_edge
                or num > self.pages - right_edge
                or (
                    num >= self.page - left_current and num <= self.page + right_current
                )
            ):
                if last + 1 != num:
                    yield None
                yield num
                last = num
        if last != self.last_page_index:
            yield None

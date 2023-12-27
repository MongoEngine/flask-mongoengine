from mongoengine.queryset import QuerySet

from flask_mongoengine.pagination.abc_pagination import ABCPagination


class KeysetPagination(ABCPagination):
    def __init__(
        self,
        iterable,
        per_page: int,
        field_filter_by: str = "_id",
        last_field_value=None,
    ):
        """
        :param iterable: iterable object .
        :param page: Required page number start from 1.
        :param per_page: Required number of documents per page.
        :param max_depth: Option for limit number of dereference documents.
        """
        self.get_page(iterable, per_page, field_filter_by, last_field_value)

    def get_page(
        self,
        iterable,
        per_page: int,
        field_filter_by: str = "_id",
        last_field_value=None,
        direction="forward",
    ):
        if last_field_value is None:
            self.page = 0
        elif getattr(self, "page", False):
            self.page += 1
        else:
            self.page = 1

        if direction == "forward":
            op = "gt"
            order_by = field_filter_by
        elif direction == "backward":
            op = "lt"
            order_by = f"-{field_filter_by}"

        else:
            raise ValueError

        self.iterable = iterable
        self.field_filter_by = field_filter_by
        # self.page = page
        self.per_page = per_page

        if isinstance(self.iterable, QuerySet):
            self.total = iterable.count()
            if self.page:
                self.items = (
                    self.iterable.filter(
                        **{f"{field_filter_by}__{op}": last_field_value}
                    )
                    .order_by(order_by)
                    .limit(self.per_page)
                )

            else:
                self.items = self.iterable.order_by(f"{field_filter_by}").limit(
                    self.per_page
                )

    def prev(self, error_out=False):
        assert NotImplementedError
        """Returns a :class:`Pagination` object for the previous page."""
        assert (
            self.iterable is not None
        ), "an object is required for this method to work"
        iterable = self.iterable
        if isinstance(iterable, QuerySet):
            iterable._skip = None
            iterable._limit = None
        self.get_page(
            iterable,
            self.per_page,
            self.field_filter_by,
            last_field_value=self.items[0][self.field_filter_by],
            direction="backward",
        )

        return self

    def next(self, error_out=False):
        """Returns a :class:`Pagination` object for the next page."""
        assert (
            self.iterable is not None
        ), "an object is required for this method to work"
        iterable = self.iterable
        if self.per_page > self.items.count():
            raise StopIteration
        if isinstance(iterable, QuerySet):
            iterable._skip = None
            iterable._limit = None
        self.get_page(
            iterable,
            self.per_page,
            self.field_filter_by,
            last_field_value=self.items[self.per_page - 1][self.field_filter_by],
        )
        return self

    def __iter__(self):
        return self

    def __next__(self):
        if getattr(self, "first_page_read", False):
            return self.next()
        else:
            self.first_page_read = True
            return self

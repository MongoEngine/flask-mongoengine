import math
from abc import ABC, abstractmethod


class ABCPagination(ABC):
    @property
    def pages(self) -> int:
        """The total number of pages"""
        return int(math.ceil(self.total / float(self.per_page)))

    @abstractmethod
    def prev(self, error_out=False):
        """Returns a :class:`Pagination` object for the previous page."""
        raise NotImplementedError

    @property
    def prev_num(self) -> int:
        """Number of the previous page."""
        return self.page - 1

    @abstractmethod
    def next(self, error_out=False):
        """Returns a :class:`Pagination` object for the next page."""
        raise NotImplementedError

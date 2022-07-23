import pytest
from werkzeug.exceptions import NotFound

from flask_mongoengine import ListFieldPagination, Pagination


def test_queryset_paginator(app, todo):
    Todo = todo
    for i in range(42):
        Todo(title=f"post: {i}").save()

    with pytest.raises(NotFound):
        Pagination(iterable=Todo.objects, page=0, per_page=10)

    with pytest.raises(NotFound):
        Pagination(iterable=Todo.objects, page=6, per_page=10)

    paginator = Pagination(Todo.objects, 1, 10)
    _test_paginator(paginator)

    for page in range(1, 10):
        for index, todo in enumerate(
            Todo.objects.paginate(page=page, per_page=5).items
        ):
            assert todo.title == f"post: {(page-1) * 5 + index}"


def test_paginate_plain_list():
    with pytest.raises(NotFound):
        Pagination(iterable=range(1, 42), page=0, per_page=10)

    with pytest.raises(NotFound):
        Pagination(iterable=range(1, 42), page=6, per_page=10)

    paginator = Pagination(range(1, 42), 1, 10)
    _test_paginator(paginator)


def test_list_field_pagination(app, todo):
    Todo = todo

    comments = [f"comment: {i}" for i in range(42)]
    todo = Todo(
        title="todo has comments",
        comments=comments,
        comment_count=len(comments),
    ).save()

    # Check without providing a total
    paginator = ListFieldPagination(Todo.objects, todo.id, "comments", 1, 10)
    _test_paginator(paginator)

    # Check with providing a total (saves a query)
    paginator = ListFieldPagination(
        Todo.objects, todo.id, "comments", 1, 10, todo.comment_count
    )
    _test_paginator(paginator)

    paginator = todo.paginate_field("comments", 1, 10)
    _test_paginator(paginator)


def _test_paginator(paginator):
    assert 5 == paginator.pages
    assert [1, 2, 3, 4, 5] == list(paginator.iter_pages())

    for i in [1, 2, 3, 4, 5]:

        if i == 1:
            assert not paginator.has_prev
            with pytest.raises(NotFound):
                paginator.prev()
        else:
            assert paginator.has_prev

        if i == 5:
            assert not paginator.has_next
            with pytest.raises(NotFound):
                paginator.next()
        else:
            assert paginator.has_next

        if i == 3:
            assert [None, 2, 3, 4, None] == list(paginator.iter_pages(0, 1, 1, 0))

        assert i == paginator.page
        assert i - 1 == paginator.prev_num
        assert i + 1 == paginator.next_num

        # Paginate to the next page
        if i < 5:
            paginator = paginator.next()

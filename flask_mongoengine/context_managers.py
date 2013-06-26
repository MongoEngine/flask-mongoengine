from flask import g, has_request_context
from mongoengine.queryset.queryset import QuerySet

orig_cursor_args = QuerySet._cursor_args.fget

def _patched_cursor_args(self):
    cursor_args = orig_cursor_args(self)

    try:
        read_preference = getattr(g, 'read_preference', None)
    except RuntimeError:  # raised when working outside of request context and FakeG hasn't been applied
        read_preference = None

    if read_preference is not None:
        if not 'read_preference' in cursor_args:
            cursor_args['read_preference'] = g.read_preference
            del cursor_args['slave_okay']
    return cursor_args

QuerySet._cursor_args = property(_patched_cursor_args)

class read_preference(object):
    def __init__(self, read_preference):
        self.read_preference = read_preference
        if not has_request_context():  # if there's no request context, create a new fake global object g
            class FakeG():
                pass
            global g
            g = FakeG()

    def __enter__(self):
        g.read_preference = self.read_preference

    def __exit__(self, t, value, traceback):
        g.read_preference = None

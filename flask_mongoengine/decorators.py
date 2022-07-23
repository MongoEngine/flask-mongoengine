import functools
import logging

try:
    import wtforms  # noqa

    wtf_installed = True
except ImportError:  # pragma: no cover
    wtf_installed = False

logger = logging.getLogger("flask_mongoengine")


def wtf_required(func):
    """Special decorator to warn user on incorrect installation."""

    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        if not wtf_installed:
            logger.error(f"WTForms not installed. Function '{func.__name__}' aborted.")
            return None

        return func(*args, **kwargs)

    return wrapped

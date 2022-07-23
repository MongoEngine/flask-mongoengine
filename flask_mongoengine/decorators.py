"""Collection of project wide decorators."""
import functools
import logging
import warnings

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


def orm_deprecated(func):
    """Warning about usage of deprecated functions, that will be removed in the future."""

    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        # TODO: Insert URL
        warnings.warn(
            (
                f"ORM module and function '{func.__name__}' are deprecated and will be "
                "removed in version 3.0.0. Please switch to form generation from full "
                "model nesting. Support and bugfixes are not available for stalled code. "
                "Please read: "
            ),
            DeprecationWarning,
            stacklevel=2,
        )

        return func(*args, **kwargs)

    return wrapped

"""Collection of project wide decorators."""
import functools
import logging
import warnings

logger = logging.getLogger("flask_mongoengine2")


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

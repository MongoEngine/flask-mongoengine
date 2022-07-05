"""Debug panel views and logic and related mongoDb event listeners."""
__all__ = ["mongo_command_logger", "MongoDebugPanel"]
import logging
import sys
from dataclasses import dataclass
from typing import List, Union

from flask import current_app
from flask_debugtoolbar.panels import DebugPanel
from jinja2 import ChoiceLoader, PackageLoader
from pymongo import monitoring

logger = logging.getLogger("flask_mongoengine")


@dataclass
class RawQueryEvent:
    # noinspection PyUnresolvedReferences
    """Responsible for parsing monitoring events to web panel interface.

    :param _event: Succeeded or Failed event object from pymongo monitoring.
    :param _start_event: Started event object from pymongo monitoring.
    :param _is_query_pass: Boolean status of db query reported by pymongo monitoring.
    """

    _event: Union[monitoring.CommandSucceededEvent, monitoring.CommandFailedEvent]
    _start_event: monitoring.CommandStartedEvent
    _is_query_pass: bool

    @property
    def time(self):
        """Query execution time."""
        return self._event.duration_micros * 0.001

    @property
    def size(self):
        """Query object size."""
        return sys.getsizeof(self.server_response, 0) / 1024

    @property
    def database(self):
        """Query database target."""
        return self._start_event.database_name

    @property
    def collection(self):
        """Query collection target."""
        return self.server_command.get(self.command_name)

    @property
    def command_name(self):
        """Query db level operation/command name."""
        return self._event.command_name

    @property
    def operation_id(self):
        """MongoDb operation_id used to match 'start' and 'final' monitoring events."""
        return self._start_event.operation_id

    @property
    def server_command(self):
        """Raw MongoDb command send to server."""
        return self._start_event.command

    @property
    def server_response(self):
        """Raw MongoDb response received from server."""
        return self._event.reply if self._is_query_pass else self._event.failure

    @property
    def request_status(self):
        """Query execution status."""
        return "Succeed" if self._is_query_pass else "Failed"


class MongoCommandLogger(monitoring.CommandListener):
    """Receive point for :class:`~.pymongo.monitoring.CommandListener` events.

    Count and parse incoming events for display in debug panel.
    """

    def __init__(self):
        self.total_time: float = 0
        self.started_operations_count: int = 0
        self.succeeded_operations_count: int = 0
        self.failed_operations_count: int = 0
        self.queries: List[RawQueryEvent] = []
        self.started_events: dict = {}

    def append_raw_query(self, event, request_status):
        """Pass 'unknown' events to parser and include final result to final list."""
        self.total_time += event.duration_micros
        start_event = self.started_events.pop(event.operation_id, {})
        self.queries.append(RawQueryEvent(event, start_event, request_status))
        logger.debug(f"Added record to 'Unknown' section: {self.queries[-1]}")

    def failed(self, event):
        """Receives 'failed' events. Required to track database answer to request."""
        logger.debug(f"Received 'Failed' event from driver: {event}")
        self.failed_operations_count += 1
        self.append_raw_query(event, False)

    def reset_tracker(self):
        """Resets all counters to default, keeping instance itself the same."""
        self.__class__.__init__(self)

    def started(self, event):
        """Receives 'started' events. Required to track original request context."""
        logger.debug(f"Received 'Started' event from driver: {event}")
        self.started_operations_count += 1
        self.started_events[event.operation_id] = event

    def succeeded(self, event):
        """Receives 'succeeded' events. Required to track database answer to request."""
        logger.debug(f"Received 'Succeeded' event from driver: {event}")
        self.succeeded_operations_count += 1
        self.append_raw_query(event, True)


mongo_command_logger = MongoCommandLogger()


def _maybe_patch_jinja_loader(jinja_env):
    """Extend jinja_env loader with flask_mongoengine templates folder."""
    package_loader = PackageLoader("flask_mongoengine", "templates")
    if not isinstance(jinja_env.loader, ChoiceLoader):
        jinja_env.loader = ChoiceLoader([jinja_env.loader, package_loader])
    elif package_loader not in jinja_env.loader.loaders:
        jinja_env.loader.loaders += [package_loader]


class MongoDebugPanel(DebugPanel):
    """Panel that shows information about MongoDB operations."""

    config_error_message = (
        "Pymongo monitoring configuration error. mongo_command_logger should be "
        "registered before database connection."
    )
    name = "MongoDB"
    has_content = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _maybe_patch_jinja_loader(self.jinja_env)

    @property
    def _context(self) -> dict:
        """Context for rendering, as property for easy testing."""
        return {
            "queries": mongo_command_logger.queries,
            "slow_query_limit": current_app.config.get(
                "MONGO_DEBUG_PANEL_SLOW_QUERY_LIMIT", 100
            ),
        }

    @property
    def is_properly_configured(self) -> bool:
        """Checks that all required watchers registered before Flask application init."""
        # noinspection PyProtectedMember
        if mongo_command_logger not in monitoring._LISTENERS.command_listeners:
            logger.error(self.config_error_message)
            return False
        return True

    def process_request(self, request):
        """Resets logger stats between each request."""
        mongo_command_logger.reset_tracker()

    def nav_title(self) -> str:
        """Debug toolbar in the bottom right corner."""
        return self.name

    def nav_subtitle(self) -> str:
        """Count operations total time."""
        if not self.is_properly_configured:
            self.has_content = False
            return self.config_error_message

        return (
            f"{mongo_command_logger.started_operations_count} operations, "
            f"in {mongo_command_logger.total_time * 0.001: .2f}ms"
        )

    def title(self) -> str:
        """Title for 'opened' debug panel window."""
        return "MongoDB Operations"

    def url(self) -> str:
        """Placeholder for internal URLs."""
        return ""

    def content(self):
        """Gathers all template required variables in one dict."""
        return self.render("panels/mongo-panel.html", self._context)

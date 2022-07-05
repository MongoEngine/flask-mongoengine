"""Debug panel views and logic and related mongoDb event listeners."""
__all__ = ["mongo_command_logger", "MongoDebugPanel"]
import logging
import sys
from dataclasses import dataclass
from typing import ClassVar, List, Sequence, Union

from flask import current_app
from flask_debugtoolbar.panels import DebugPanel
from jinja2 import ChoiceLoader, PackageLoader
from pymongo import monitoring

logger = logging.getLogger("flask_mongoengine")


@dataclass
class BaseLoggedEvents:
    # noinspection PyUnresolvedReferences
    """
    Base pymongo event pair parser data class.

    Responsible for parsing shared data for all subclasses.
    Debug panel web interface use only not 'private' instance properties.

    :param _event: Succeeded or Failed event object from pymongo monitoring.
    :param _start_event: Started event object from pymongo monitoring.
    :param _is_query_pass: Boolean status of db query reported by pymongo monitoring.
    :param supported_operations: Class level collection of events, supported by
        dataclass parser. Used in events routing. Except for :class:`UnknownQueryEvent`
    """

    _event: Union[monitoring.CommandSucceededEvent, monitoring.CommandFailedEvent]
    _start_event: monitoring.CommandStartedEvent
    _is_query_pass: bool
    supported_operations: ClassVar[Sequence[str]]

    @property
    def _succeeded_event(self):
        """Internal helper to get 'succeeded' event object. Just for code readability."""
        return self._event if self._is_query_pass else None

    @property
    def _failed_event(self):
        """Internal helper to get 'failed' event object. Just for code readability."""
        return None if self._is_query_pass else self._event

    @property
    def time(self):
        """Shared web interface data: query execution time."""
        return self._event.duration_micros * 0.001

    @property
    def size(self):
        """Shared web interface data: success query object size or zero for failed."""
        return sys.getsizeof(self._event.reply, 0) / 1024 if self._is_query_pass else 0

    @property
    def database(self):
        """Shared web interface data: query database target."""
        return self._start_event.database_name

    @property
    def collection(self):
        """Shared web interface data: query collection target."""
        return self._start_event.command.get(self.operation)

    @property
    def operation(self):
        """Shared web interface data: query db level operation/command name."""
        return self._event.command_name

    @property
    def request_status(self):
        """Shared web interface data: query execution status."""
        return "Succeed" if self._is_query_pass else "Failed"


class DeleteQueryEvent(BaseLoggedEvents):
    """
    Handle 'removes' only related properties parsing.

    For init parameters and full explanation check base class :class:`BaseLoggedEvents`.
    """

    supported_operations = ("delete", "dropDatabase")

    @property
    def _delete_data(self):
        """Internal extractor for 'delete' MongoDb statements."""
        if self.operation != "delete":
            return {}
        try:
            return self._start_event.command.get("deletes", [])[0]
        except IndexError:
            return {}

    @property
    def filter(self):
        """Filter used before operation."""
        return self._delete_data.get("q", "")


class InsertQueryEvent(BaseLoggedEvents):
    """
    Handle 'insert' only related properties parsing.

    For init parameters and full explanation check base class :class:`BaseLoggedEvents`.
    """

    supported_operations = ("insert", "create")

    @property
    def filter(self):
        """Filter used before operation."""
        return None

    @property
    def document(self):
        """Document inserted to database with operation."""
        return self._start_event.command.get("documents")


class FindQueryEvent(BaseLoggedEvents):
    """
    Handle 'find' only related properties parsing.

    For init parameters and full explanation check base class :class:`BaseLoggedEvents`.
    """

    supported_operations = ["find"]

    @property
    def sorting(self):
        """Internal sorting statement extractor."""
        _sorting = self._start_event.command.get("sort")
        return _sorting.to_dict() if _sorting is not None else None

    @property
    def filter(self):
        """Filter used before operation."""
        return self._start_event.command.get("filter")

    @property
    def skip(self):
        """Query 'skip' value."""
        return self._start_event.command.get("skip")

    @property
    def limit(self):
        """Query 'limit' value."""
        return self._start_event.command.get("limit")

    @property
    def data(self):
        """Documents returned by operation."""
        return (
            self._event.reply.get("cursor", {}).get("firstBatch")
            if self._is_query_pass
            else None
        )


class UpdateQueryEvent(BaseLoggedEvents):
    """
    Handle 'update' only related properties parsing.

    For init parameters and full explanation check base class :class:`BaseLoggedEvents`.
    """

    supported_operations = ["update"]

    @property
    def _update_data(self):
        """Internal extractor for 'update' MongoDb statements."""
        if self.operation != "update":
            return {}
        try:
            return self._start_event.command.get("updates", [])[0]
        except IndexError:
            return {}

    @property
    def filter(self):
        """Filter used before operation."""
        return self._update_data.get("q") if self._update_data else None

    @property
    def updates(self):
        """Content of operation statement."""
        return self._update_data.get("u") if self._update_data else None

    @property
    def multi(self):
        """Is operation launched with 'multi' flag."""
        return self._update_data.get("multi", False) if self._update_data else False

    @property
    def upsert(self):
        """Is operation launched with 'upsert' flag."""
        return self._update_data.get("upsert", False) if self._update_data else False


class UnknownQueryEvent(BaseLoggedEvents):
    """
    Handle 'unknown' only related properties parsing.

    For init parameters and full explanation check base class :class:`BaseLoggedEvents`.
    """

    supported_operations = []


class MongoCommandLogger(monitoring.CommandListener):
    """Receive point for :class:`~.pymongo.monitoring.CommandListener` events.

    Count and parse incoming events for display in debug panel.
    """

    def __init__(self):
        self.total_time: float = 0
        self.started_operations_count: int = 0
        self.succeeded_operations_count: int = 0
        self.failed_operations_count: int = 0
        self.queries: List = []
        self.inserts: List = []
        self.updates: List = []
        self.deletes: List = []
        self.unknown: List = []
        self.started_events: dict = {}

    def append_delete_query(self, event, start_event, request_status):
        """Pass 'remove' events to parser and include final result to final list."""
        self.deletes.append(DeleteQueryEvent(event, start_event, request_status))
        logger.debug(f"Added record to 'deletes' section: {self.deletes[-1]}")

    def append_find_query(self, event, start_event, request_status):
        """Pass 'find' events to parser and include final result to final list."""
        self.queries.append(FindQueryEvent(event, start_event, request_status))
        logger.debug(f"Added record to 'Query' section: {self.queries[-1]}")

    def append_insert_query(self, event, start_event, request_status):
        """Pass 'insert' events to parser and include final result to final list."""
        self.inserts.append(InsertQueryEvent(event, start_event, request_status))
        logger.debug(f"Added record to 'Insert' section: {self.inserts[-1]}")

    def append_update_query(self, event, start_event, request_status):
        """Pass 'update' events to parser and include final result to final list."""
        self.updates.append(UpdateQueryEvent(event, start_event, request_status))
        logger.debug(f"Added record to 'Updates' section: {self.updates[-1]}")

    def failed(self, event):
        """Receives 'failed' events. Required to track database answer to request."""
        logger.debug(f"Received 'Failed' event from driver: {event}")
        self.failed_operations_count += 1
        self.route_db_response(event, False)

    def reset_tracker(self):
        """Resets all counters to default, keeping instance itself the same."""
        self.__class__.__init__(self)

    def route_db_response(self, event, request_status):
        """Route response to correct response parser. Match started and final events."""
        self.total_time += event.duration_micros
        start_event = self.started_events.pop(event.operation_id, {})

        if event.command_name in DeleteQueryEvent.supported_operations:
            self.append_delete_query(event, start_event, request_status)
        elif event.command_name in InsertQueryEvent.supported_operations:
            self.append_insert_query(event, start_event, request_status)
        elif event.command_name in FindQueryEvent.supported_operations:
            self.append_find_query(event, start_event, request_status)
        elif event.command_name in UpdateQueryEvent.supported_operations:
            self.append_update_query(event, start_event, request_status)

    def started(self, event):
        """Receives 'started' events. Required to track original request context."""
        logger.debug(f"Received 'Started' event from driver: {event}")
        self.started_operations_count += 1
        self.started_events[event.operation_id] = event

    def succeeded(self, event):
        """Receives 'succeeded' events. Required to track database answer to request."""
        logger.debug(f"Received 'Succeeded' event from driver: {event}")
        self.succeeded_operations_count += 1
        self.route_db_response(event, True)


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
            "inserts": mongo_command_logger.inserts,
            "updates": mongo_command_logger.updates,
            "deletes": mongo_command_logger.deletes,
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

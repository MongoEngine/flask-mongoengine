"""Debug panel views and logic and related mongoDb event listeners."""
import sys
from typing import List

from flask import current_app
from flask_debugtoolbar.panels import DebugPanel
from jinja2 import ChoiceLoader, PackageLoader
from pymongo import monitoring


class DebugPanelCommandLogger(monitoring.CommandListener):
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
        """Parse 'remove' events to debug panel supported format."""
        deletes = start_event.command.get("deletes", [])
        if deletes:
            for obj in deletes:
                self.deletes.append(
                    {
                        "time": event.duration_micros * 0.001,
                        "size": sys.getsizeof(event.reply, 0) / 1024,
                        "operation": event.command_name,
                        "collection": start_event.command.get("delete"),
                        "filter": obj.get("q", ""),
                        "request_status": "Succeed" if request_status else "Failed",
                    }
                )

    def append_find_query(self, event, start_event, request_status):
        """Parse 'find' events to debug panel supported format."""
        sorting = start_event.command.get("sort")
        self.queries.append(
            {
                "time": event.duration_micros * 0.001,
                "size": sys.getsizeof(event.reply, 0) / 1024,
                "operation": event.command_name,
                "collection": start_event.command.get("find"),
                "filter": start_event.command.get("filter"),
                "sorting": sorting.to_dict() if sorting is not None else None,
                "skip": start_event.command.get("skip"),
                "limit": start_event.command.get("limit"),
                "data": event.reply.get("cursor", {}).get("firstBatch"),
                "request_status": "Succeed" if request_status else "Failed",
            }
        )

    def append_insert_query(self, event, start_event, request_status):
        """Parse 'insert' events to debug panel supported format."""
        self.inserts.append(
            {
                "time": event.duration_micros * 0.001,
                "size": sys.getsizeof(event.reply, 0) / 1024,
                "operation": event.command_name,
                "collection": start_event.command.get("insert"),
                "filter": None,
                "document": start_event.command.get("documents"),
                "request_status": "Succeed" if request_status else "Failed",
            }
        )

    def append_update_query(self, event, start_event, request_status):
        """Parse 'update' events to debug panel supported format."""
        updates = start_event.command.get("updates", [])
        if updates:
            for update in updates:
                self.updates.append(
                    {
                        "time": event.duration_micros * 0.001,
                        "size": sys.getsizeof(event.reply, 0) / 1024,
                        "operation": event.command_name,
                        "collection": start_event.command.get("update"),
                        "filter": update.get("q"),
                        "updates": update.get("u"),
                        "multi": update.get("multi", False),
                        "upsert": update.get("upsert", False),
                        "request_status": "Succeed" if request_status else "Failed",
                    }
                )
        else:
            self.updates.append(
                {
                    "time": event.duration_micros * 0.001,
                    "size": sys.getsizeof(event.reply, 0) / 1024,
                    "operation": event.command_name,
                    "collection": start_event.command.get("find"),
                    "filter": start_event.command.get("filter", ""),
                    "data": start_event.command.get("updates"),
                    "request_status": "Succeed" if request_status else "Failed",
                }
            )

    def failed(self, event):
        """Receives 'failed' events. Required to track database answer to request."""
        self.failed_operations_count += 1
        self.route_db_response(event, False)

    def reset_tracker(self):
        """Resets all counters to default, keeping instance itself the same."""
        self.__class__.__init__(self)

    def route_db_response(self, event, request_status):
        """Route response to correct response parser. Match started and final events."""
        self.total_time += event.duration_micros
        start_event = self.started_events.pop(event.operation_id, {})

        if event.command_name == "delete":
            self.append_delete_query(event, start_event, request_status)
        elif event.command_name == "insert":
            self.append_insert_query(event, start_event, request_status)
        elif event.command_name == "find":
            self.append_find_query(event, start_event, request_status)
        elif event.command_name == "update":
            self.append_update_query(event, start_event, request_status)

    def started(self, event):
        """Receives 'started' events. Required to track original request context."""
        if event.command_name == "delete":
            print(f"Command started command: {event.command}")
            print(f"Command started database_name: {event.database_name}")

        self.started_operations_count += 1
        self.started_events[event.operation_id] = event

    def succeeded(self, event):
        """Receives 'succeeded' events. Required to track database answer to request."""
        if event.command_name == "delete":
            print(f"Command succeeded duration_micros {event.duration_micros}")
            print(f"Command succeeded reply {event.reply}")

        self.succeeded_operations_count += 1
        self.route_db_response(event, True)


command_logger = DebugPanelCommandLogger()
monitoring.register(command_logger)


def _maybe_patch_jinja_loader(jinja_env):
    """Extend jinja_env loader with flask_mongoengine templates folder."""
    package_loader = PackageLoader("flask_mongoengine", "templates")
    if not isinstance(jinja_env.loader, ChoiceLoader):
        jinja_env.loader = ChoiceLoader([jinja_env.loader, package_loader])
    elif package_loader not in jinja_env.loader.loaders:
        jinja_env.loader.loaders.append(package_loader)


class MongoDebugPanel(DebugPanel):
    """Panel that shows information about MongoDB operations."""

    name = "MongoDB"
    has_content = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _maybe_patch_jinja_loader(self.jinja_env)

    def process_request(self, request):
        """Resets logger stats between each request."""
        command_logger.reset_tracker()

    def nav_title(self) -> str:
        """Debug toolbar in the bottom right corner."""
        return self.name

    def nav_subtitle(self) -> str:
        """Count operations total time."""
        return (
            f"{command_logger.started_operations_count} operations, "
            f"in {command_logger.total_time*0.001: .2f}ms"
        )

    def title(self) -> str:
        """Title for 'opened' debug panel window."""
        return "MongoDB Operations"

    def url(self) -> str:
        """Placeholder for internal URLs."""
        return ""

    def content(self):
        """Gathers all template required variables in one dict."""
        context = {
            "queries": command_logger.queries,
            "inserts": command_logger.inserts,
            "updates": command_logger.updates,
            "deletes": command_logger.deletes,
            "slow_query_limit": current_app.config.get(
                "MONGO_DEBUG_PANEL_SLOW_QUERY_LIMIT", 100
            ),
        }
        return self.render("panels/mongo-panel.html", context)

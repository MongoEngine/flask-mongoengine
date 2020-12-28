from flask import current_app
from flask_debugtoolbar.panels import DebugPanel
from jinja2 import ChoiceLoader, PackageLoader

from flask_mongoengine import operation_tracker

package_loader = PackageLoader("flask_mongoengine", "templates")


def _maybe_patch_jinja_loader(jinja_env):
    """Patch the jinja_env loader to include flaskext.mongoengine
    templates folder if necessary.
    """
    if not isinstance(jinja_env.loader, ChoiceLoader):
        jinja_env.loader = ChoiceLoader([jinja_env.loader, package_loader])
    elif package_loader not in jinja_env.loader.loaders:
        jinja_env.loader.loaders.append(package_loader)


class MongoDebugPanel(DebugPanel):
    """Panel that shows information about MongoDB operations."""

    name = "MongoDB"
    has_content = True

    def __init__(self, *args, **kwargs):
        super(MongoDebugPanel, self).__init__(*args, **kwargs)
        _maybe_patch_jinja_loader(self.jinja_env)
        operation_tracker.install_tracker()

    def process_request(self, request):
        operation_tracker.reset()

    def nav_title(self) -> str:
        return self.name

    def nav_subtitle(self) -> str:
        """Count operations and total time, excluding any toolbar related operations."""
        total_time = 0
        operations_count = 0
        for query_type in {"queries", "inserts", "updates", "removes"}:
            for operation in getattr(operation_tracker, query_type):
                if operation.get("internal", False):
                    continue

                operations_count += 1
                total_time += operation.get("time", 0)

        return "{0} operations in {1:.2f}ms".format(operations_count, total_time)

    def title(self) -> str:
        return "MongoDB Operations"

    def url(self) -> str:
        return ""

    def content(self):
        """Gather all template required variables in one dict."""
        context = {
            "queries": operation_tracker.queries,
            "inserts": operation_tracker.inserts,
            "updates": operation_tracker.updates,
            "removes": operation_tracker.removes,
            "slow_query_limit": current_app.config.get(
                "MONGO_DEBUG_PANEL_SLOW_QUERY_LIMIT", 100
            ),
        }
        return self.render("panels/mongo-panel.html", context)

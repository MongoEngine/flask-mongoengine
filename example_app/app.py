import flask
from flask_debugtoolbar import DebugToolbarExtension
from models import db
from pymongo import monitoring
from views import index, pagination

from flask_mongoengine.panels import mongo_command_logger

app = flask.Flask("example_app")
# Working multidatabase settings example
app.config["MONGODB_SETTINGS"] = [
    {"db": "example_app", "host": "mongo", "alias": "default"},
    {
        "MONGODB_DB": "example_app_2",
        "MONGODB_HOST": "mongo",
        "MONGODB_ALIAS": "secondary",
    },
]
app.config["TESTING"] = True
app.config["SECRET_KEY"] = "flask+mongoengine=<3"
app.debug = True
app.config["DEBUG_TB_PANELS"] = (
    "flask_debugtoolbar.panels.config_vars.ConfigVarsDebugPanel",
    "flask_debugtoolbar.panels.g.GDebugPanel",
    "flask_debugtoolbar.panels.headers.HeaderDebugPanel",
    "flask_debugtoolbar.panels.logger.LoggingPanel",
    "flask_debugtoolbar.panels.profiler.ProfilerDebugPanel",
    "flask_debugtoolbar.panels.request_vars.RequestVarsDebugPanel",
    "flask_debugtoolbar.panels.route_list.RouteListDebugPanel",
    "flask_debugtoolbar.panels.template.TemplateDebugPanel",
    "flask_debugtoolbar.panels.timer.TimerDebugPanel",
    "flask_debugtoolbar.panels.versions.VersionDebugPanel",
    "flask_mongoengine.panels.MongoDebugPanel",
)
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
DebugToolbarExtension(app)
monitoring.register(mongo_command_logger)
db.init_app(app)


app.add_url_rule("/", view_func=index)
app.add_url_rule("/pagination", view_func=pagination)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

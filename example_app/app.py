import flask
from flask_debugtoolbar import DebugToolbarExtension
from pymongo import monitoring

from example_app import views
from example_app.boolean_demo import boolean_demo_view
from example_app.dates_demo import dates_demo_view
from example_app.dict_demo import dict_demo_view
from example_app.models import db
from example_app.numbers_demo import numbers_demo_view
from example_app.strings_demo import strings_demo_view
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


app.add_url_rule("/", view_func=views.index, methods=["GET", "POST"])
app.add_url_rule("/pagination", view_func=views.pagination, methods=["GET", "POST"])
app.add_url_rule("/strings", view_func=strings_demo_view, methods=["GET", "POST"])
app.add_url_rule("/strings/<pk>/", view_func=strings_demo_view, methods=["GET", "POST"])
app.add_url_rule("/numbers", view_func=numbers_demo_view, methods=["GET", "POST"])
app.add_url_rule("/numbers/<pk>/", view_func=numbers_demo_view, methods=["GET", "POST"])
app.add_url_rule("/dates", view_func=dates_demo_view, methods=["GET", "POST"])
app.add_url_rule("/dates/<pk>/", view_func=dates_demo_view, methods=["GET", "POST"])
app.add_url_rule("/bool", view_func=boolean_demo_view, methods=["GET", "POST"])
app.add_url_rule("/bool/<pk>/", view_func=boolean_demo_view, methods=["GET", "POST"])
app.add_url_rule("/dict", view_func=dict_demo_view, methods=["GET", "POST"])
app.add_url_rule("/dict/<pk>/", view_func=dict_demo_view, methods=["GET", "POST"])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

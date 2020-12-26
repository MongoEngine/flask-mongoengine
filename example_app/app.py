import flask
from flask_debugtoolbar import DebugToolbarExtension

from models import db
from views import index, pagination

app = flask.Flask(__name__)
app.config.from_object(__name__)
app.config["MONGODB_SETTINGS"] = {"DB": "testing", "host": "mongo"}
app.config["TESTING"] = True
app.config["SECRET_KEY"] = "flask+mongoengine=<3"
app.debug = True
app.config["DEBUG_TB_PANELS"] = (
    "flask_debugtoolbar.panels.versions.VersionDebugPanel",
    "flask_debugtoolbar.panels.timer.TimerDebugPanel",
    "flask_debugtoolbar.panels.headers.HeaderDebugPanel",
    "flask_debugtoolbar.panels.request_vars.RequestVarsDebugPanel",
    "flask_debugtoolbar.panels.template.TemplateDebugPanel",
    "flask_debugtoolbar.panels.logger.LoggingPanel",
    "flask_mongoengine.panels.MongoDebugPanel",
)
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False

db.init_app(app)

DebugToolbarExtension(app)

app.add_url_rule("/", view_func=index)
app.add_url_rule("/pagination", view_func=pagination)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

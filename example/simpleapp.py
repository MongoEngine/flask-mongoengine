from __future__ import with_statement

import os
import sys
import datetime
import flask

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '../')))

from random import choice

from flask.ext.mongoengine import MongoEngine
from flask.ext.mongoengine.wtf import model_form
from flask_debugtoolbar import DebugToolbarExtension

app = flask.Flask(__name__)
app.config.from_object(__name__)
app.config['MONGODB_SETTINGS'] = {'DB': 'testing'}
app.config['TESTING'] = True
app.config['SECRET_KEY'] = 'flask+mongoengine=<3'
app.debug = True
app.config['DEBUG_TB_PANELS'] = (
             'flask.ext.debugtoolbar.panels.versions.VersionDebugPanel',
             'flask.ext.debugtoolbar.panels.timer.TimerDebugPanel',
             'flask.ext.debugtoolbar.panels.headers.HeaderDebugPanel',
             'flask.ext.debugtoolbar.panels.request_vars.RequestVarsDebugPanel',
             'flask.ext.debugtoolbar.panels.template.TemplateDebugPanel',
             'flask.ext.debugtoolbar.panels.logger.LoggingPanel',
             'flask.ext.mongoengine.panels.MongoDebugPanel'
             )

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

db = MongoEngine()
db.init_app(app)

DebugToolbarExtension(app)


class Todo(db.Document):
    title = db.StringField(max_length=60)
    text = db.StringField()
    done = db.BooleanField(default=False)
    pub_date = db.DateTimeField(default=datetime.datetime.now)

@app.route('/')
def index():
    # As a list to test debug toolbar
    Todo.objects().delete()  # Removes
    Todo(title="Simple todo A", text="12345678910").save()  # Insert
    Todo(title="Simple todo B", text="12345678910").save()  # Insert
    Todo.objects(title__contains="B").update(set__text="Hello world")  # Update
    todos = list(Todo.objects[:10])
    todos = Todo.objects.all()
    return flask.render_template('index.html', todos=todos)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000)

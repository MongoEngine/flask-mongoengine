# Flask configuration

Flask-mongoengine does not provide any configuration defaults. User is responsible
for setting up correct database settings, to exclude any possible misconfiguration
and data corruption.

There are several options to set connection. Please note, that all except
recommended are deprecated and may be removed in future versions, to lower code base
complexity and bugs. If you use any deprecated connection settings approach, you should
update your application configuration.

By default, flask-mongoengine2 open the connection when extension is instantiated,
but you can configure it to open connection only on first database access by setting
the ``'connect'`` dictionary parameter or its ``MONGODB_CONNECT`` flat equivalent to
``False``.

```{note}
Due lack of developers we are unable to answer/solve not recommended connection methods
errors. Please switch to recommended method before posting any issue. Thank you.
```

## Recommended: List of dictionaries settings

Recommended way for setting up connections is to set ``MONGODB_SETTINGS`` in you
application config. ``MONGODB_SETTINGS`` is a list of dictionaries, where each
dictionary is configuration for individual database (for systems with multi-database)
use.

Each dictionary in ``MONGODB_SETTINGS`` will be passed to {func}`mongoengine.connect`,
which will bypass settings to {func}`mongoengine.register_connection`. All settings
related to {func}`mongoengine.connect` and {func}`mongoengine.register_connection` will
be extracted by mentioned functions, any other keyword arguments will be silently
followed to {class}`pymongo.mongo_client.MongoClient`.

This allows complete and flexible database configuration.

Example:

```python
import flask
from flask_mongoengine2 import MongoEngine

db = MongoEngine()
app = flask.Flask("example_app")
app.config["MONGODB_SETTINGS"] = [
    {
        "db": "project1",
        "host": "localhost",
        "port": 27017,
        "alias": "default",
    }
]
db.init_app(app)
```

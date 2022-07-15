# Flask configuration

Flask-mongoengine does not provide any configuration defaults. User is responsible
for setting up correct database settings, to exclude any possible misconfiguration
and data corruption.

There are several options to set connection. Please note, that all except
recommended are deprecated and may be removed in future versions, to lower code base
complexity and bugs. If you use any deprecated connection settings approach, you should
update your application configuration.

By default, flask-mongoengine open the connection when extension is instantiated,
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
from flask_mongoengine import MongoEngine

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

## Deprecated: Passing database configuration to MongoEngine class

```{eval-rst}
.. deprecated:: 2.0.0
```

You can pass database dictionary of dictionaries directly to {class}`.MongoEngine`
class initialization. Lists of settings not supported.

```python
import flask
from flask_mongoengine import MongoEngine

db_config = {
    "db": "project1",
    "host": "localhost",
    "port": 27017,
    "alias": "default",
}
db = MongoEngine(config=db_config)
app = flask.Flask("example_app")

db.init_app(app)
```

## Deprecated: Passing database configuration to MongoEngine.init_app method

```{eval-rst}
.. deprecated:: 2.0.0
```

You can pass database dictionary of dictionaries directly to
{func}`flask_mongoengine.MongoEngine.init_app` class initialization. Lists of
settings not supported.

```python
import flask
from flask_mongoengine import MongoEngine

db_config = {
    "db": "project1",
    "host": "localhost",
    "port": 27017,
    "alias": "default",
}
db = MongoEngine()
app = flask.Flask("example_app")

db.init_app(app, config=db_config)
```

## Deprecated: MONGODB_ inside MONGODB_SETTINGS dictionary

```{eval-rst}
.. deprecated:: 2.0.0
```

Flask-mongoengine will cut off ``MONGODB_`` prefix from any parameters, specified
inside ``MONGODB_SETTINGS`` dictionary. This is historical behaviour, but may be
removed in the future. Providing such settings may raise config errors, when parent
packets implement case-sensitive keyword arguments checks. Check issue [#451] for
example historical problem.

Currently, we are handling all possible case-sensitive keyword settings and related
users errors (based on pymongo 4.1.1), but amount of such settings may be increased
in future pymongo versions.

Usage of recommended settings approach completely remove this possible problem.

## Deprecated: URI style settings

```{eval-rst}
.. deprecated:: 2.0.0
```

URI style connections supported as supply the uri as the ``host`` in the
``MONGODB_SETTINGS`` dictionary in ``app.config``.

```{warning}
It is not recommended to use URI style settings, as URI style settings parsed and
manupulated in all parent functions/methods. This may lead to unexpected behaviour when
parent packages versions changed.
```

```{warning}
Database name from uri has priority over name. (MongoEngine behaviour).
```

If uri presents and doesn't contain database name db setting entirely ignore and db
name set to ``test``:

```python
import flask
from flask_mongoengine import MongoEngine

db = MongoEngine()
app = flask.Flask("example_app")
app.config['MONGODB_SETTINGS'] = {
    'db': 'project1',
    'host': 'mongodb://localhost/database_name'
}
db.init_app(app)
```

## Deprecated: Flat MONGODB_ style configuration settings

```{eval-rst}
.. deprecated:: 2.0.0
```

Connection settings may also be provided individually by prefixing the setting with
``MONGODB_`` in the ``app.config``:

```python
import flask
from flask_mongoengine import MongoEngine

db = MongoEngine()
app = flask.Flask("example_app")
app.config['MONGODB_DB'] = 'project1'
app.config['MONGODB_HOST'] = '192.168.1.35'
app.config['MONGODB_PORT'] = 12345
app.config['MONGODB_USERNAME'] = 'webapp'
app.config['MONGODB_PASSWORD'] = 'pwd123'
db.init_app(app)
```

This method does not support multi-database installations.

By default, flask-mongoengine open the connection when extension is instantiated,
but you can configure it to open connection only on first database access by setting
the ``MONGODB_SETTINGS['connect']`` parameter or its ``MONGODB_CONNECT`` flat
equivalent to ``False``.

[#451]: https://github.com/MongoEngine/flask-mongoengine/issues/451

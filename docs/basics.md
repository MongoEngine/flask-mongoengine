# Installation and basic usage

## Pre-requisite

Make sure you have ``wheel`` installed:

```bash
pip install wheel
```

## Installing Flask-MongoEngine

Install with **pip**:

```bash
pip install flask-mongoengine
```

## Configuration

Basic setup is easy, just fetch the extension::

```python
from flask import Flask
from flask_mongoengine import MongoEngine

app = Flask(__name__)
app.config.from_pyfile('the-config.cfg')
db = MongoEngine(app)
```

Or, if you are setting up your database before your app is initialized, as is the case
with application factories:

```python
from flask import Flask
from flask_mongoengine import MongoEngine
db = MongoEngine()
...
app = Flask(__name__)
app.config.from_pyfile('the-config.cfg')
db.init_app(app)
```

By default, Flask-MongoEngine assumes that the mongo database instance is running
on ``localhost`` on port ``27017``, and you wish to connect to the database
named ``test``.

If MongoDB is running elsewhere, you should provide the ``host`` and ``port`` settings
in  the ``MONGODB_SETTINGS`` dictionary wih `app.`config``:

```python
app.config['MONGODB_SETTINGS'] = {
    'db': 'project1',
    'host': '192.168.1.35',
    'port': 12345
}
```

If the database requires authentication, the ``username`` and ``password``
arguments should be provided ``MONGODB_SETTINGS`` dictionary wih ``app.config``:

```python
app.config['MONGODB_SETTINGS'] = {
    'db': 'project1',
    'username':'webapp',
    'password':'pwd123'
}
```

URI style connections are also supported, just supply the uri as the ``host``
in the `'MONGODB_SETTINGS'` dictionary with ``app.config``.

```{warning}
Database name from uri has priority over name.
```

If uri presents and doesn't contain database name db setting entirely ignore and db
name set to ``test``:

```python
app.config['MONGODB_SETTINGS'] = {
    'db': 'project1',
    'host': 'mongodb://localhost/database_name'
}
```

Connection settings may also be provided individually by prefixing the setting with
``MONGODB_`` in the ``app.config``:

```python
app.config['MONGODB_DB'] = 'project1'
app.config['MONGODB_HOST'] = '192.168.1.35'
app.config['MONGODB_PORT'] = 12345
app.config['MONGODB_USERNAME'] = 'webapp'
app.config['MONGODB_PASSWORD'] = 'pwd123'
```

By default, flask-mongoengine open the connection when extension is instantiated,
but you can configure it to open connection only on first database access by setting
the ``MONGODB_SETTINGS['connect']`` parameter or its ``MONGODB_CONNECT`` flat
equivalent to ``False``:

```python
app.config['MONGODB_SETTINGS'] = {
    'host': 'mongodb://localhost/database_name',
    'connect': False,
}
# or
app.config['MONGODB_CONNECT'] = False
```

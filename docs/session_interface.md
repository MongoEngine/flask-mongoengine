# Session Interface

```{warning}
Soon to be deprecated
```

To use MongoEngine as your session store simple configure the session interface:

```python
from flask_mongoengine import MongoEngine, MongoEngineSessionInterface

app = Flask(__name__)
db = MongoEngine(app)
app.session_interface = MongoEngineSessionInterface(db)
```

## How to migrate to Flask-session

### Step 1

Read at <https://flask-session.readthedocs.io/en/latest/index.html>
How to implement

```python

from flask_mongoengine import MongoEngine
from flask_session import Session

app = Flask(__name__)
db = MongoEngine(app)

# app.session_interface = MongoEngineSessionInterface(db)
app.config['SESSION_MONGODB'] = db.connection
app.config['SESSION_MONGODB_DB'] = '<YOUR_DEFAULT_DB>'
app.config['SESSION_MONGODB_COLLECT'] = 'session'
Session(app)

app.session_interface.cls.objects.update(rename__data='val')
```

### Step 2

Refactor the collection field by flask-session name
Run once

```python

from flask_mongoengine import MongoEngine, MongoEngineSessionInterface

app = Flask(__name__)
db = MongoEngine(app)

app.session_interface = MongoEngineSessionInterface(db)

app.session_interface.cls.objects.update(rename__data='val')
```

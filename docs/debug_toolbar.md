# Debug Toolbar Panel

```{eval-rst}
.. image:: _static/debugtoolbar.png
  :target: #debug-toolbar-panel
```

If you use the Flask-DebugToolbar you can add
`'flask_mongoengine.panels.MongoDebugPanel'` to the `DEBUG_TB_PANELS` config
list and then it will automatically track your queries::

```python
    from flask import Flask
    from flask_debugtoolbar import DebugToolbarExtension

    app = Flask(__name__)
    app.config['DEBUG_TB_PANELS'] = ['flask_mongoengine.panels.MongoDebugPanel']
    db = MongoEngine(app)
    toolbar = DebugToolbarExtension(app)
```

# Custom Json Encoder

flask-mongoengine have option to add custom encoder for flask
By this way you can handle encoding special object

Examples:

```python
from flask_mongoengine.json import MongoEngineJSONProvider
class CustomJSONEncoder(MongoEngineJSONProvider):
    @staticmethod
    def default(obj):
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, Decimal128):
            return str(obj)
        return MongoEngineJSONProvider.default(obj)


# Tell your flask app to use your customised JSON encoder


app.json_provider_class = CustomJSONEncoder
app.json = app.json_provider_class(app)

```

from flask.json import JSONEncoder
from bson import json_util
from mongoengine.base import BaseDocument
from mongoengine.queryset.base import BaseQuerySet

class MongoEngineJSONEncoder(JSONEncoder):
    '''
    A JSONEncoder which provides serialization of MongoEngine
    documents and querysets.
    '''
    def default(self,obj):
        if isinstance(obj,BaseDocument):
            return json_util._json_convert(obj.to_mongo())
        elif isinstance(obj,BaseQuerySet):
            return json_util._json_convert(obj.as_pymongo())
        return JSONEncoder.default(self, obj)


def overide_json_encoder(app):
    '''
    A function to dynamically create a new MongoEngineJSONEncoder class
    based upon a custom base class.
    This function allows us to combine MongoEngine serialization with
    any changes to Flask's JSONEncoder which a user may have made
    prior to calling init_app.

    NOTE: This does not cover situations where users override
    an instance's json_encoder after calling init_app. 
    '''
    class MongoEngineJSONEncoder(app.json_encoder):
        def default(self,obj):
            if isinstance(obj,BaseDocument):
                return json_util._json_convert(obj.to_mongo())
            elif isinstance(obj,BaseQuerySet):
                return json_util._json_convert(obj.as_pymongo())
            return app.json_encoder.default(self, obj)
    app.json_encoder = MongoEngineJSONEncoder

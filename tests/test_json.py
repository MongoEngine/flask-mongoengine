import sys
sys.path[0:0] = [""]

import unittest
import datetime
import flask

from flask.ext.mongoengine import MongoEngine
from flask.ext.mongoengine.json import MongoEngineJSONEncoder


class DummyEncoder(flask.json.JSONEncoder):
    '''
    An example encoder which a user may create and override
    the apps json_encoder with.
    This class is a NO-OP, but used to test proper inheritance.
    '''


class JSONAppTestCase(unittest.TestCase):

    def dictContains(self,superset,subset):
        for k,v in subset.items():
            if not superset[k] == v:
                return False
        return True

    def assertDictContains(self,superset,subset):
        return self.assertTrue(self.dictContains(superset,subset))

    def setUp(self):
        app = flask.Flask(__name__)
        app.config['MONGODB_DB'] = 'testing'
        app.config['TESTING'] = True
        app.json_encoder = DummyEncoder
        db = MongoEngine()
        db.init_app(app)

        self.app = app
        self.db = db

    def test_inheritance(self):
        self.assertTrue(issubclass(self.app.json_encoder, DummyEncoder))
        json_encoder_name = self.app.json_encoder.__name__

        # Since the class is dynamically derrived, must compare class names
        # rather than class objects.
        self.assertEqual(json_encoder_name, 'MongoEngineJSONEncoder')

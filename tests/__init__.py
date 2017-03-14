import unittest
import flask
import mongoengine


class FlaskMongoEngineTestCase(unittest.TestCase):
    """Parent class of all test cases"""

    def setUp(self):
        self.app = flask.Flask(__name__)
        self.app.config['MONGODB_DB'] = 'test_db'
        self.app.config['TESTING'] = True
        self.ctx = self.app.app_context()
        self.ctx.push()
        # Mongoengine keep a global state of the connections that must be
        # reset before each test.
        # Given it doesn't expose any method to get the list of registered
        # connections, we have to do the cleaning by hand...
        mongoengine.connection._connection_settings.clear()
        mongoengine.connection._connections.clear()
        mongoengine.connection._dbs.clear()

    def tearDown(self):
        self.ctx.pop()

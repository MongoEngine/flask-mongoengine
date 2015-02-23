import flask
import unittest

class FlaskMongoEngineTestCase(unittest.TestCase):
    """Parent class of all test cases"""

    def setUp(self):
        self.app = flask.Flask(__name__)
        self.app.config['MONGODB_DB'] = 'testing'
        self.app.config['TESTING'] = True
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

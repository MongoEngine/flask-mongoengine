import unittest

import flask
from flask_mongoengine import current_mongoengine_instance


class FlaskMongoEngineTestCase(unittest.TestCase):
    """Parent class of all test cases"""

    def setUp(self):
        self.app = flask.Flask(__name__)
        self.app.config['MONGODB_DB'] = 'test_db'
        self.app.config['TESTING'] = True
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        me_instance = current_mongoengine_instance()
        if me_instance:
            me_instance.disconnect()
        self.ctx.pop()

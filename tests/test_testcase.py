import sys
sys.path[0:0] = [""]

import unittest
import flask

from flask.ext.mongoengine import MongoEngine
from flask.ext.mongoengine.test import tc_factory


def create_flask_app(db_name):
    app = flask.Flask(__name__)
    app.config['MONGODB_SETTINGS'] = {"DB": db_name}
    app = app
    db = MongoEngine()
    db.init_app(app)

    return db


class TestCaseClassFactory(unittest.TestCase):

    def setUp(self):
        self.db_name = 'testing'
        self.db = create_flask_app(self.db_name)

    def test_it_should_provide_a_TestCase_class(self):
        expected_class = tc_factory(self.db)
        self.assertEqual("TestCase", expected_class.__name__)


if __name__ == '__main__':
    unittest.main()

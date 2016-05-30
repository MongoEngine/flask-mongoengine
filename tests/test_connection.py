import unittest
import mongomock
import mongoengine
from pymongo.errors import InvalidURI
from distutils.version import StrictVersion
from flask_mongoengine import MongoEngine
from tests import FlaskMongoEngineTestCase


class ConnectionTestCase(FlaskMongoEngineTestCase):

    def test_ignore_parse_uri_if_testing_true_and_uses_mongomock_schema(self):
        self.app.config['TESTING'] = True
        self.app.config['MONGODB_ALIAS'] = 'unittest'
        self.app.config['MONGODB_HOST'] = 'mongomock://localhost'

        if StrictVersion(mongoengine.__version__) >= StrictVersion('0.10.6'):
            db = MongoEngine(self.app)
            self.assertTrue(isinstance(db.connection, mongomock.MongoClient))

    def test_parse_uri_if_testing_true_and_not_uses_mongomock_schema(self):
        self.app.config['TESTING'] = True
        self.app.config['MONGODB_ALIAS'] = 'unittest'
        self.app.config['MONGODB_HOST'] = 'mongo://localhost'

        self.assertRaises(InvalidURI, MongoEngine, self.app)

    def test_parse_uri_if_testing_not_true(self):
        self.app.config['TESTING'] = False
        self.app.config['MONGODB_ALIAS'] = 'unittest'
        self.app.config['MONGODB_HOST'] = 'mongomock://localhost'

        self.assertRaises(InvalidURI, MongoEngine, self.app)

    def test_parse_uri_without_database_name(self):
        self.app.config['TESTING'] = False
        self.app.config['MONGODB_HOST'] = 'mongodb://localhost'

        self.assertRaises(ValueError, MongoEngine, self.app)

if __name__ == '__main__':
    unittest.main()

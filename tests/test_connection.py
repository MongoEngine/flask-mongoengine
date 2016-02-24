import unittest
import mongomock
from pymongo.errors import InvalidURI
from flask.ext.mongoengine import MongoEngine
from tests import FlaskMongoEngineTestCase

class ConnectionTestCase(FlaskMongoEngineTestCase):

    def test_ignore_parse_uri_if_testing_true_and_use_mongomock_schema(self):
        self.app.config['TESTING'] = True
        self.app.config['MONGODB_ALIAS'] = 'unittest'
        self.app.config['MONGODB_HOST'] = 'mongomock://localhost'
        db = MongoEngine(self.app)

        self.assertIsInstance(db.connection, mongomock.MongoClient)

    def test_parse_uri_if_testing_true_and_not_use_mongomock_schema(self):
    	self.app.config['TESTING'] = True
    	self.app.config['MONGODB_ALIAS'] = 'unittest'
    	self.app.config['MONGODB_HOST'] = 'mongo://localhost'

        with self.assertRaises(InvalidURI):
            db = MongoEngine(self.app)

    def test_parse_uri_if_testing_is_not_true(self):
    	self.app.config['TESTING'] = False
    	self.app.config['MONGODB_ALIAS'] = 'unittest'
        self.app.config['MONGODB_HOST'] = 'mongomock://localhost'
        
        with self.assertRaises(InvalidURI):
            db = MongoEngine(self.app)

if __name__ == '__main__':
    unittest.main()

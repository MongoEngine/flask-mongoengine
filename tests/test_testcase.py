import sys
sys.path[0:0] = [""]

import os
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


class RunningTestsBehaviour(unittest.TestCase):

    def setUp(self):
        self.db_name = 'testing'
        self.test_db_name = "test_" + self.db_name
        self.db = create_flask_app(self.db_name)
        self.test_app = None
        self.TestCase = tc_factory(self.db)
        self.db_connection = self.db.connection[self.test_db_name]

    def _running_a_test(self, test_function):
        function_name = test_function.__name__
        setattr(self.TestCase, function_name, test_function)
        suite = unittest.TestSuite()
        suite.addTest(self.TestCase(function_name))
        with open(os.devnull, 'w') as devnull:
            unittest.TextTestRunner(stream=devnull).run(suite)

    def test_it_should_provide_a_testing_app_and_a_testing_db(self):
        def fake_test(*args):
            _self = args[0]
            self.test_app = _self.test_app

        self._running_a_test(fake_test)

        test_app = self.test_app
        self.assertTrue(hasattr(test_app, "config"))
        self.assertTrue("MONGODB_SETTINGS" in test_app.config.keys())
        MONGODB_SETTINGS = test_app.config["MONGODB_SETTINGS"]['DB']
        self.assertEqual("test_" + self.db_name, MONGODB_SETTINGS)

    def test_it_should_clean_up_data_when_test_raised(self):
        def ERROR_test(*args):
            class SimpleDocument(self.db.Document):
                pass

            simple_document = SimpleDocument()
            simple_document.save()

            raise Exception("ERROR!")

        self._running_a_test(ERROR_test)

        collections = self.db_connection.collection_names()
        self.assertFalse("simple_document" in collections)

    def test_it_should_clean_up_data_after_test_was_executed(self):
        def dirtying_test(*args):
            class SimpleDocument(self.db.Document):
                pass

            simple_document = SimpleDocument()
            simple_document.save()

        self._running_a_test(dirtying_test)

        collections = self.db_connection.collection_names()
        self.assertFalse("simple_document" in collections)

    def test_saving_on_test_database(self):
        db_connection = self.db_connection
        self.collections = None
        self.count = None

        def saving_test(*args):
            class SimpleDocument(self.db.Document):
                pass

            simple_document = SimpleDocument()
            simple_document.save()

            self.collections = db_connection.collection_names()
            a_document_collection = db_connection.simple_document
            self.count = a_document_collection.count()

        self._running_a_test(saving_test)

        self.assertTrue("simple_document" in self.collections)
        self.assertEqual(1, self.count)


if __name__ == '__main__':
    unittest.main()

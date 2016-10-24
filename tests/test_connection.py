import mongoengine
import mongomock
import pymongo
from pymongo.errors import InvalidURI

from flask_mongoengine import InvalidSettingsError, MongoEngine
from tests import FlaskMongoEngineTestCase


class ConnectionTestCase(FlaskMongoEngineTestCase):

    def ensure_mongomock_connection(self):
        db = MongoEngine(self.app)
        self.assertTrue(isinstance(db.connection.client, mongomock.MongoClient))

    def test_mongomock_connection_request_on_most_recent_mongoengine(self):
        self.app.config['TESTING'] = True
        self.app.config['MONGODB_ALIAS'] = 'unittest_0'
        self.app.config['MONGODB_HOST'] = 'mongomock://localhost'

        if mongoengine.VERSION >= (0, 10, 6):
            self.ensure_mongomock_connection()

    def test_mongomock_connection_request_on_most_old_mongoengine(self):
        self.app.config['TESTING'] = 'True'
        self.assertRaises(InvalidSettingsError, MongoEngine, self.app)

        self.app.config['TESTING'] = True
        self.app.config['MONGODB_ALIAS'] = 'unittest_1'
        self.app.config['MONGODB_HOST'] = 'mongomock://localhost'

        if mongoengine.VERSION < (0, 10, 6):
            self.ensure_mongomock_connection()

    def test_live_connection(self):
        db = MongoEngine()
        self.app.config['TEMP_DB'] = True
        self.app.config['MONGODB_SETTINGS'] = {
            'HOST': 'localhost',
            'PORT': 27017,
            'USERNAME': None,
            'PASSWORD': None,
            'DB': 'test'
        }

        self._do_persist(db)

    def _do_persist(self, db):
        class Todo(db.Document):
            title = db.StringField(max_length=60)
            text = db.StringField()
            done = db.BooleanField(default=False)

        db.init_app(self.app)
        Todo.drop_collection()

        # Test persist
        todo = Todo()
        todo.text = "Sample"
        todo.title = "Testing"
        todo.done = True
        s_todo = todo.save()

        f_to = Todo.objects().first()
        self.assertEqual(s_todo.title, f_to.title)

    def test_multiple_connections(self):
        db = MongoEngine()
        self.app.config['TESTING'] = True
        self.app.config['MONGODB_SETTINGS'] = [
            {
                'ALIAS': 'default',
                'DB': 'my_db1',
                'HOST': 'localhost',
                'PORT': 27017
            },
            {
                "ALIAS": "my_db2",
                "DB": 'my_db2',
                "HOST": 'localhost',
                "PORT": 27017
            },
        ]

        class Todo(db.Document):
            title = db.StringField(max_length=60)
            text = db.StringField()
            done = db.BooleanField(default=False)
            meta = {"db_alias": "my_db2"}

        db.init_app(self.app)
        Todo.drop_collection()

        # Switch DB
        from mongoengine.context_managers import switch_db
        with switch_db(Todo, 'default') as Todo:
            todo = Todo()
            todo.text = "Sample"
            todo.title = "Testing"
            todo.done = True
            s_todo = todo.save()

            f_to = Todo.objects().first()
            self.assertEqual(s_todo.title, f_to.title)

    def test_mongodb_temp_instance(self):
        # String value used instead of boolean
        self.app.config['TESTING'] = True
        self.app.config['TEMP_DB'] = 'True'
        self.assertRaises(InvalidSettingsError, MongoEngine, self.app)

        self.app.config['TEMP_DB'] = True
        db = MongoEngine(self.app)
        self.assertTrue(isinstance(db.connection, pymongo.MongoClient))

    def test_InvalidURI_exception_connections(self):
        # Invalid URI
        self.app.config['TESTING'] = True
        self.app.config['MONGODB_ALIAS'] = 'unittest_2'
        self.app.config['MONGODB_HOST'] = 'mongo://localhost'
        self.assertRaises(InvalidURI, MongoEngine, self.app)

    def test_parse_uri_if_testing_true_and_not_uses_mongomock_schema(self):
        # TESTING is false but mongomock URI
        self.app.config['TESTING'] = False
        self.app.config['MONGODB_ALIAS'] = 'unittest_3'
        self.app.config['MONGODB_HOST'] = 'mongomock://localhost'
        self.assertRaises(InvalidURI, MongoEngine, self.app)

    def test_temp_db_with_false_testing(self):
        # TEMP_DB is set to true but testing is false
        self.app.config['TESTING'] = False
        self.app.config['TEMP_DB'] = True
        self.app.config['MONGODB_ALIAS'] = 'unittest_4'
        self.assertRaises(InvalidSettingsError, MongoEngine, self.app)

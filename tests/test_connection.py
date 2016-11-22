from pymongo.errors import InvalidURI

from flask_mongoengine import MongoEngine
from tests import FlaskMongoEngineTestCase


class ConnectionTestCase(FlaskMongoEngineTestCase):

    def test_live_connection(self):
        db = MongoEngine()
        self.app.config['MONGODB_SETTINGS'] = {
            'HOST': 'localhost',
            'PORT': 27017,
            'DB': 'flask_mongoengine_test_db'
        }
        self._do_persist(db)

    def test_live_connection_with_uri_string(self):
        db = MongoEngine()
        self.app.config['MONGO_URI'] = 'mongodb://localhost:27017/flask_mongoengine_test_db'
        self._do_persist(db)

    def _do_persist(self, db):
        """Initialize test Flask application and persist some data in
        MongoDB, ultimately asserting that the connection works.
        """
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
        from mongoengine.context_managers import switch_db

        db = MongoEngine()
        self.app.config['MONGODB_SETTINGS'] = [
            {
                'ALIAS': 'default',
                'DB': 'flask_mongoengine_test_db_1',
                'HOST': 'localhost',
                'PORT': 27017
            },
            {
                'ALIAS': 'alternative',
                'DB': 'flask_mongoengine_test_db_2',
                'HOST': 'localhost',
                'PORT': 27017
            },
        ]

        class Todo(db.Document):
            title = db.StringField(max_length=60)
            text = db.StringField()
            done = db.BooleanField(default=False)
            meta = {'db_alias': 'alternative'}

        db.init_app(self.app)
        Todo.drop_collection()

        # Test saving a doc via the default connection
        with switch_db(Todo, 'default') as Todo:
            todo = Todo()
            todo.text = "Sample"
            todo.title = "Testing"
            todo.done = True
            s_todo = todo.save()

            f_to = Todo.objects().first()
            self.assertEqual(s_todo.title, f_to.title)

        # Make sure the doc doesn't exist in the alternative db
        with switch_db(Todo, 'alternative') as Todo:
            doc = Todo.objects().first()
            self.assertEqual(doc, None)

        # Make sure switching back to the default connection shows the doc
        with switch_db(Todo, 'default') as Todo:
            doc = Todo.objects().first()
            self.assertNotEqual(doc, None)

    def test_connection_with_invalid_uri(self):
        self.app.config['MONGODB_ALIAS'] = 'unittest_2'
        self.app.config['MONGODB_HOST'] = 'mongo://localhost'
        self.assertRaises(InvalidURI, MongoEngine, self.app)

    def test_connection_kwargs(self):
        self.app.config['MONGODB_SETTINGS'] = {
            'DB': 'flask_mongoengine_testing_tz_aware',
            'alias': 'tz_aware_true',
            'TZ_AWARE': True
        }
        db = MongoEngine()
        db.init_app(self.app)
        self.assertTrue(db.connection.client.codec_options.tz_aware)

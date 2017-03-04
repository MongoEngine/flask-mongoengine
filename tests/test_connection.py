from mongoengine.context_managers import switch_db
import pymongo
from pymongo.errors import InvalidURI
from pymongo.read_preferences import ReadPreference

from flask_mongoengine import MongoEngine

from tests import FlaskMongoEngineTestCase


class ConnectionTestCase(FlaskMongoEngineTestCase):

    def _do_persist(self, db):
        """Initialize a test Flask application and persist some data in
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

    def test_simple_connection(self):
        """Make sure a simple connection to a standalone MongoDB works."""
        db = MongoEngine()
        self.app.config['MONGODB_SETTINGS'] = {
            'ALIAS': 'simple_conn',
            'HOST': 'localhost',
            'PORT': 27017,
            'DB': 'flask_mongoengine_test_db'
        }
        self._do_persist(db)

    def test_host_as_uri_string(self):
        """Make sure we can connect to a standalone MongoDB if we specify
        the host as a MongoDB URI.
        """
        db = MongoEngine()
        self.app.config['MONGODB_HOST'] = 'mongodb://localhost:27017/flask_mongoengine_test_db'
        self._do_persist(db)

    def test_mongomock_host_as_uri_string(self):
        """Make sure we can connect to the mongomock object if we specify
        the host as a mongomock URI.
        """
        db = MongoEngine()
        self.app.config['MONGODB_HOST'] = 'mongomock://localhost:27017/flask_mongoengine_test_db'
        self._do_persist(db)

    def test_host_as_list(self):
        """Make sure MONGODB_HOST can be a list hosts."""
        db = MongoEngine()
        self.app.config['MONGODB_SETTINGS'] = {
            'ALIAS': 'host_list',
            'HOST': ['localhost:27017'],
        }
        self._do_persist(db)

    def test_multiple_connections(self):
        """Make sure establishing multiple connections to a standalone
        MongoDB and switching between them works.
        """
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
        """Make sure connecting via an invalid URI raises an InvalidURI
        exception.
        """
        self.app.config['MONGODB_HOST'] = 'mongo://localhost'
        self.assertRaises(InvalidURI, MongoEngine, self.app)

    def test_connection_kwargs(self):
        """Make sure additional connection kwargs work."""

        # Figure out whether to use "MAX_POOL_SIZE" or "MAXPOOLSIZE" based
        # on PyMongo version (former was changed to the latter as described
        # in https://jira.mongodb.org/browse/PYTHON-854)
        # TODO remove once PyMongo < 3.0 support is dropped
        if pymongo.version_tuple[0] >= 3:
            MAX_POOL_SIZE_KEY = 'MAXPOOLSIZE'
        else:
            MAX_POOL_SIZE_KEY = 'MAX_POOL_SIZE'

        self.app.config['MONGODB_SETTINGS'] = {
            'ALIAS': 'tz_aware_true',
            'DB': 'flask_mongoengine_testing_tz_aware',
            'TZ_AWARE': True,
            'READ_PREFERENCE': ReadPreference.SECONDARY,
            MAX_POOL_SIZE_KEY: 10,
        }
        db = MongoEngine()
        db.init_app(self.app)
        self.assertTrue(db.connection.codec_options.tz_aware)
        self.assertEqual(db.connection.max_pool_size, 10)
        self.assertEqual(
            db.connection.read_preference,
            ReadPreference.SECONDARY
        )

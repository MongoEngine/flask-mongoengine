import mongoengine
from mongoengine.context_managers import switch_db
from nose import SkipTest
from nose.tools import assert_raises
import pymongo
from pymongo.errors import InvalidURI
from pymongo.read_preferences import ReadPreference

from flask_mongoengine import MongoEngine

from tests import FlaskMongoEngineTestCase


class ConnectionTestCase(FlaskMongoEngineTestCase):

    def _do_persist(self, db, alias=None):
        """Initialize a test Flask application and persist some data in
        MongoDB, ultimately asserting that the connection works.
        """
        if alias:
            class Todo(db.Document):
                meta = {'db_alias': alias}
                title = db.StringField(max_length=60)
                text = db.StringField()
                done = db.BooleanField(default=False)
        else:
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
        self._do_persist(db, alias='simple_conn')

    def test_host_as_uri_string(self):
        """Make sure we can connect to a standalone MongoDB if we specify
        the host as a MongoDB URI.
        """
        db = MongoEngine()
        self.app.config['MONGODB_HOST'] = 'mongodb://localhost:27017/flask_mongoengine_test_db'
        self._do_persist(db)

    def test_mongomock_host_as_uri_string(self):
        """Make sure we switch to mongomock if we specify the host as a mongomock URI.
        """
        if mongoengine.VERSION < (0, 9, 0):
            raise SkipTest('Mongomock not supported for mongoengine < 0.9.0')
        db = MongoEngine()
        self.app.config['MONGODB_HOST'] = 'mongomock://localhost:27017/flask_mongoengine_test_db'
        with assert_raises(RuntimeError) as exc:
            self._do_persist(db)
        assert str(exc.exception) == 'You need mongomock installed to mock MongoEngine.'

    def test_mongomock_as_param(self):
        """Make sure we switch to mongomock when providing IS_MOCK option.
        """
        if mongoengine.VERSION < (0, 9, 0):
            raise SkipTest('Mongomock not supported for mongoengine < 0.9.0')
        db = MongoEngine()
        self.app.config['MONGODB_SETTINGS'] = {
            'ALIAS': 'simple_conn',
            'HOST': 'localhost',
            'PORT': 27017,
            'DB': 'flask_mongoengine_test_db',
            'IS_MOCK': True
        }
        with assert_raises(RuntimeError) as exc:
            self._do_persist(db, alias='simple_conn')
        assert str(exc.exception) == 'You need mongomock installed to mock MongoEngine.'

    def test_host_as_list(self):
        """Make sure MONGODB_HOST can be a list hosts."""
        db = MongoEngine()
        self.app.config['MONGODB_SETTINGS'] = {
            'ALIAS': 'host_list',
            'HOST': ['localhost:27017'],
            'DB': 'flask_mongoengine_test_db'
        }
        self._do_persist(db, alias='host_list')

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

    def test_ingnored_mongodb_prefix_config(self):
        """Config starting by MONGODB_ but not used by flask-mongoengine
        should be ignored.
        """
        db = MongoEngine()
        self.app.config['MONGODB_HOST'] = 'mongodb://localhost:27017/flask_mongoengine_test_db_prod'
        # Invalid host, should trigger exception if used
        self.app.config['MONGODB_TEST_HOST'] = 'dummy://localhost:27017/test'
        self._do_persist(db)

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

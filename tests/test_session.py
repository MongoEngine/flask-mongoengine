import unittest

from flask import session
from flask_mongoengine import MongoEngine, MongoEngineSessionInterface
from tests import FlaskMongoEngineTestCase


class SessionTestCase(FlaskMongoEngineTestCase):

    def setUp(self):
        super(SessionTestCase, self).setUp()
        self.db_name = 'testing'
        self.app.config['MONGODB_DB'] = self.db_name
        self.app.config['TESTING'] = True
        db = MongoEngine(self.app)
        self.app.session_interface = MongoEngineSessionInterface(db)

        @self.app.route('/')
        def index():
            session["a"] = "hello session"
            return session["a"]

        @self.app.route('/check-session')
        def check_session():
            return "session: %s" % session["a"]

        @self.app.route('/check-session-database')
        def check_session_database():
            sessions = self.app.session_interface.cls.objects.count()
            return "sessions: %s" % sessions

        self.db = db

    def tearDown(self):
        try:
            self.db.connection.drop_database(self.db_name)
        except:
            self.db.connection.client.drop_database(self.db_name)

    def test_setting_session(self):
        c = self.app.test_client()
        resp = c.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertEquals(resp.data.decode('utf-8'), 'hello session')

        resp = c.get('/check-session')
        self.assertEqual(resp.status_code, 200)
        self.assertEquals(resp.data.decode('utf-8'), 'session: hello session')

        resp = c.get('/check-session-database')
        self.assertEqual(resp.status_code, 200)
        self.assertEquals(resp.data.decode('utf-8'), 'sessions: 1')

if __name__ == '__main__':
    unittest.main()

import sys

import unittest
import datetime
import flask

from flask.ext.mongoengine import MongoEngine
from . import FlaskMongoEngineTestCase


class BasicAppTestCase(FlaskMongoEngineTestCase):

    def setUp(self):
        super(BasicAppTestCase, self).setUp()
        db = MongoEngine()

        class Todo(db.Document):
            title = db.StringField(max_length=60)
            text = db.StringField()
            done = db.BooleanField(default=False)
            pub_date = db.DateTimeField(default=datetime.datetime.now)

        db.init_app(self.app)

        Todo.drop_collection()
        self.Todo = Todo

        @self.app.route('/')
        def index():
            return '\n'.join(x.title for x in self.Todo.objects)

        @self.app.route('/add', methods=['POST'])
        def add():
            form = flask.request.form
            todo = self.Todo(title=form['title'],
                             text=form['text'])
            todo.save()
            return 'added'

        @self.app.route('/show/<id>/')
        def show(id):
            todo = self.Todo.objects.get_or_404(id=id)
            return '\n'.join([todo.title, todo.text])

        self.db = db

    def test_connection_kwargs(self):
        self.app.config['MONGODB_SETTINGS'] = {
            'DB': 'testing_tz_aware',
            'ALIAS': 'tz_aware_true',
            'TZ_AWARE': True
        }
        self.app.config['TESTING'] = True
        db = MongoEngine()
        db.init_app(self.app)
        self.assertTrue(db.connection.tz_aware)

        # PyMongo defaults to tz_aware = True so we have to explicitly turn
        # it off.
        self.app.config['MONGODB_SETTINGS'] = {
            'DB': 'testing',
            'ALIAS': 'tz_aware_false',
            'TZ_AWARE': False
        }
        db = MongoEngine()
        db.init_app(self.app)
        self.assertFalse(db.connection.tz_aware)

    def test_connection_kwargs_as_list(self):
        self.app.config['MONGODB_SETTINGS'] = [{
            'DB': 'testing_tz_aware',
            'alias': 'tz_aware_true',
            'TZ_AWARE': True
        }, {
            'DB': 'testing_tz_aware_off',
            'alias': 'tz_aware_false',
            'TZ_AWARE': False
        }]
        self.app.config['TESTING'] = True
        db = MongoEngine()
        db.init_app(self.app)
        self.assertTrue(db.connection['tz_aware_true'].tz_aware)
        self.assertFalse(db.connection['tz_aware_false'].tz_aware)

    def test_connection_default(self):
        self.app.config['MONGODB_SETTINGS'] = {}
        self.app.config['TESTING'] = True

        db = MongoEngine()
        db.init_app(self.app)

        self.app.config['TESTING'] = True
        db = MongoEngine()
        db.init_app(self.app)

    def test_with_id(self):
        c = self.app.test_client()
        resp = c.get('/show/38783728378090/')
        self.assertEqual(resp.status_code, 404)

        c.post('/add', data={'title': 'First Item', 'text': 'The text'})

        resp = c.get('/show/%s/' % self.Todo.objects.first_or_404().id)
        self.assertEqual(resp.status_code, 200)
        self.assertEquals(resp.data.decode('utf-8'), 'First Item\nThe text')

    def test_basic_insert(self):
        c = self.app.test_client()
        c.post('/add', data={'title': 'First Item', 'text': 'The text'})
        c.post('/add', data={'title': '2nd Item', 'text': 'The text'})
        rv = c.get('/')
        self.assertEquals(rv.data.decode('utf-8'), 'First Item\n2nd Item')

    def test_request_context(self):
        with self.app.test_request_context():
            todo = self.Todo(title='Test', text='test')
            todo.save()
            self.assertEqual(self.Todo.objects.count(), 1)

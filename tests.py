from __future__ import with_statement

import unittest
import datetime
import flask

from flask.ext import mongoengine
from flask.ext.mongoengine.wtf import model_form

from mongoengine import queryset_manager


def make_todo_model(db):
    class Todo(db.Document):
        title = db.StringField(max_length=60)
        text = db.StringField()
        done = db.BooleanField(default=False)
        pub_date = db.DateTimeField(default=datetime.datetime.now)
    return Todo


class BasicAppTestCase(unittest.TestCase):

    def setUp(self):
        app = flask.Flask(__name__)
        app.config['MONGODB_DB'] = 'testing'
        app.config['TESTING'] = True
        db = mongoengine.MongoEngine()
        self.Todo = make_todo_model(db)

        db.init_app(app)

        @app.route('/')
        def index():
            return '\n'.join(x.title for x in self.Todo.objects)

        @app.route('/add', methods=['POST'])
        def add():
            form = flask.request.form
            todo = self.Todo(title=form['title'],
                             text=form['text'])
            todo.save()
            return 'added'

        @app.route('/show/<id>/')
        def show(id):
            todo = self.Todo.objects.get_or_404(id=id)
            return '\n'.join([todo.title, todo.text])

        self.app = app
        self.db = db

    def tearDown(self):
        for todo in self.Todo.objects:
            todo.delete()

    def test_with_id(self):
        c = self.app.test_client()
        resp = c.get('/show/38783728378090/')
        self.assertEqual(resp.status_code, 404)

        c.post('/add', data={'title': 'First Item', 'text': 'The text'})

        resp = c.get('/show/%s/' % self.Todo.objects.first_or_404().id)
        self.assertEqual(resp.status_code, 200)
        self.assertEquals(resp.data, 'First Item\nThe text')

    def test_basic_insert(self):
        c = self.app.test_client()
        c.post('/add', data={'title': 'First Item', 'text': 'The text'})
        c.post('/add', data={'title': '2nd Item', 'text': 'The text'})
        rv = c.get('/')
        self.assertEquals(rv.data, 'First Item\n2nd Item')

    def test_request_context(self):
        with self.app.test_request_context():
            todo = self.Todo(title='Test', text='test')
            todo.save()
            self.assertEqual(self.Todo.objects.count(), 1)


class WTFormsAppTestCase(unittest.TestCase):

    def setUp(self):
        self.db_name = 'testing'

        app = flask.Flask(__name__)
        app.config['MONGODB_DB'] = self.db_name
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        self.db = mongoengine.MongoEngine()
        self.db.init_app(app)

    def tearDown(self):
        self.db.connection.drop_database(self.db_name)

    def test_model_form(self):
        db = self.db

        class BlogPost(db.Document):
            title = db.StringField(required=True, max_length=200)
            posted = db.DateTimeField(default=datetime.datetime.now)
            tags = db.ListField(db.StringField(max_length=50))

        class TextPost(BlogPost):
            content = db.StringField(required=True)

        class LinkPost(BlogPost):
            url = db.StringField(required=True)

        # Create a text-based post
        TextPostForm = model_form(TextPost)

        form = TextPostForm(**{
            'title': 'Using MongoEngine',
            'tags': ['mongodb', 'mongoengine']})

        self.assertFalse(form.validate())

        form = TextPostForm(**{
            'title': 'Using MongoEngine',
            'content': 'See the tutorial',
            'tags': ['mongodb', 'mongoengine']})

        self.assertTrue(form.validate())
        form.save()

        self.assertEquals(BlogPost.objects.count(), 1)

    def test_model_form_with_custom_query_set(self):

        db = self.db

        class Dog(db.Document):
            breed = db.StringField()

            @queryset_manager
            def large_objects(cls, queryset):
                return queryset(breed__in = ['german sheppard', 'wolfhound'])

        class DogOwner(db.Document):
            dog = db.ReferenceField(Dog)

        big_dogs = [Dog(breed="german sheppard"), Dog(breed="wolfhound")]
        dogs = [Dog(breed="poodle")] + big_dogs
        for dog in dogs:
            dog.save()

        BigDogForm = model_form(DogOwner, field_args={'dog': {'queryset' : Dog.large_objects} })

        form = BigDogForm()

        self.assertEqual( big_dogs, [d[1] for d in form.dog.iter_choices()] )

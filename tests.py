from __future__ import with_statement

import unittest
import datetime
import flask
import wtforms

from bson import ObjectId
from werkzeug.datastructures import MultiDict
from flask.ext.mongoengine import MongoEngine
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
        db = MongoEngine()
        self.Todo = make_todo_model(db)

        db.init_app(app)

        self.Todo.drop_collection()

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

    def test_connection_kwargs(self):
        app = flask.Flask(__name__)
        app.config['MONGODB_SETTINGS'] = {
            'DB': 'testing_tz_aware',
            'alias': 'tz_aware_true',
            'TZ_AWARE': True,
        }
        app.config['TESTING'] = True
        db = MongoEngine()
        db.init_app(app)
        self.assertTrue(db.connection.tz_aware)

        app.config['MONGODB_SETTINGS'] = {
            'DB': 'testing',
            'alias': 'tz_aware_false',
        }
        db.init_app(app)
        self.assertFalse(db.connection.tz_aware)

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
        self.app = app
        self.db = MongoEngine()
        self.db.init_app(app)

    def tearDown(self):
        self.db.connection.drop_database(self.db_name)

    def test_model_form(self):
        with self.app.test_request_context('/'):
            db = self.db

            class BlogPost(db.Document):
                meta = {'allow_inheritance': True}
                title = db.StringField(required=True, max_length=200)
                posted = db.DateTimeField(default=datetime.datetime.now)
                tags = db.ListField(db.StringField())

            class TextPost(BlogPost):
                email = db.EmailField(required=False)
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

            self.assertEquals(BlogPost.objects.first().title, 'Using MongoEngine')
            self.assertEquals(BlogPost.objects.count(), 1)

            form = TextPostForm(**{
                'title': 'Using Flask-MongoEngine',
                'content': 'See the tutorial',
                'tags': ['flask', 'mongodb', 'mongoengine']})

            self.assertTrue(form.validate())
            form.save()
            self.assertEquals(BlogPost.objects.count(), 2)

            post = BlogPost.objects(title="Using Flask-MongoEngine").get()

            form = TextPostForm(MultiDict({
                'title': 'Using Flask-MongoEngine',
                'content': 'See the tutorial',
                'tags-0': 'flask',
                'tags-1': 'mongodb',
                'tags-2': 'mongoengine',
                'tags-3': 'flask-mongoengine',
            }), instance=post)
            self.assertTrue(form.validate())
            form.save()
            post = post.reload()

            self.assertEqual(post.tags, ['flask', 'mongodb', 'mongoengine', 'flask-mongoengine'])

    def test_model_form_with_custom_query_set(self):
        with self.app.test_request_context('/'):
            db = self.db

            class Dog(db.Document):
                breed = db.StringField()

                @queryset_manager
                def large_objects(cls, queryset):
                    return queryset(breed__in=['german sheppard', 'wolfhound'])

            class DogOwner(db.Document):
                dog = db.ReferenceField(Dog)

            big_dogs = [Dog(breed="german sheppard"), Dog(breed="wolfhound")]
            dogs = [Dog(breed="poodle")] + big_dogs
            for dog in dogs:
                dog.save()

            BigDogForm = model_form(DogOwner, field_args={'dog': {'queryset': Dog.large_objects}})

            form = BigDogForm(dog=big_dogs[0])
            self.assertTrue(form.validate())
            self.assertEqual(big_dogs, [d[1] for d in form.dog.iter_choices()])

    def test_modelselectfield(self):
        with self.app.test_request_context('/'):
            db = self.db

            class Dog(db.Document):
                name = db.StringField()

            class DogOwner(db.Document):
                dog = db.ReferenceField(Dog)

            DogOwnerForm = model_form(DogOwner)

            dog = Dog(name="fido")
            dog.save()

            form = DogOwnerForm(dog=dog)
            self.assertTrue(form.validate())

            self.assertEqual(wtforms.widgets.Select, type(form.dog.widget))
            self.assertEqual(False, form.dog.widget.multiple)

    def test_modelselectfield_multiple(self):
        with self.app.test_request_context('/'):
            db = self.db

            class Dog(db.Document):
                name = db.StringField()

            class DogOwner(db.Document):
                dogs = db.ListField(db.ReferenceField(Dog))

            DogOwnerForm = model_form(DogOwner)

            dogs = [Dog(name="fido"), Dog(name="rex")]
            for dog in dogs:
                dog.save()

            form = DogOwnerForm(dogs=dogs)
            self.assertTrue(form.validate())

            self.assertEqual(wtforms.widgets.Select, type(form.dogs.widget))
            self.assertEqual(True, form.dogs.widget.multiple)

            # Validate if both dogs are selected
            choices = list(form.dogs)
            self.assertEqual(len(choices), 2)
            self.assertTrue(choices[0].checked)
            self.assertTrue(choices[1].checked)

    def test_passwordfield(self):
        with self.app.test_request_context('/'):
            db = self.db

            class User(db.Document):
                password = db.StringField()

            UserForm = model_form(User, field_args={'password': {'password': True}})
            form = UserForm(password='12345')
            self.assertEqual(wtforms.widgets.PasswordInput, type(form.password.widget))

    def test_unique_with(self):

        with self.app.test_request_context('/'):
            db = self.db

            class Item (db.Document):
                owner_id = db.ObjectIdField(required=True)
                owner_item_id = db.StringField(required=True, unique_with='owner_id')

            Item.drop_collection()

            object_id = ObjectId()
            Item(object_id, owner_item_id="1").save()

            try:
                Item(object_id, owner_item_id="1").save()
                self.fail("Should have raised duplicate key error")
            except:
                pass

            self.assertEqual(1, Item.objects.count())

if __name__ == '__main__':
    unittest.main()

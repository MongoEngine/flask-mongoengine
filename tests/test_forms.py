import datetime
import re
import unittest

import bson
import flask
from mongoengine import queryset_manager
from werkzeug.datastructures import MultiDict
import wtforms

from flask_mongoengine import MongoEngine
from flask_mongoengine.wtf import model_form
from tests import FlaskMongoEngineTestCase


class WTFormsAppTestCase(FlaskMongoEngineTestCase):

    def setUp(self):
        super(WTFormsAppTestCase, self).setUp()
        self.db_name = 'test_db'
        self.app.config['MONGODB_DB'] = self.db_name
        self.app.config['TESTING'] = True
        # For Flask-WTF < 0.9
        self.app.config['CSRF_ENABLED'] = False
        # For Flask-WTF >= 0.9
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.db = MongoEngine()
        self.db.init_app(self.app)

    def tearDown(self):
        try:
            self.db.connection.drop_database(self.db_name)
        except:
            self.db.connection.client.drop_database(self.db_name)

    def test_binaryfield(self):

        with self.app.test_request_context('/'):
            db = self.db

            class Binary(db.Document):
                binary = db.BinaryField()

            BinaryForm = model_form(Binary)
            form = BinaryForm(MultiDict({'binary': '1'}))
            self.assertTrue(form.validate())
            form.save()

    def test_choices_coerce(self):

        with self.app.test_request_context('/'):
            db = self.db

            CHOICES = ((1, "blue"), (2, "red"))

            class MyChoices(db.Document):
                pill = db.IntField(choices=CHOICES)

            MyChoicesForm = model_form(MyChoices)
            form = MyChoicesForm(MultiDict({"pill": "1"}))
            self.assertTrue(form.validate())
            form.save()
            self.assertEqual(MyChoices.objects.first().pill, 1)

    def test_list_choices_coerce(self):

        with self.app.test_request_context('/'):
            db = self.db

            CHOICES = ((1, "blue"), (2, "red"))

            class MyChoices(db.Document):
                pill = db.ListField(db.IntField(choices=CHOICES))

            MyChoicesForm = model_form(MyChoices)
            form = MyChoicesForm(MultiDict({"pill": "1"}))
            self.assertTrue(form.validate())
            form.save()
            self.assertEqual(MyChoices.objects.first().pill[0], 1)

    def test_emailfield(self):

        with self.app.test_request_context('/'):
            db = self.db

            class Email(db.Document):
                email = db.EmailField(required=False)

            EmailForm = model_form(Email)
            form = EmailForm(instance=Email())
            self.assertFalse("None" in "%s" % form.email)
            self.assertTrue(form.validate())

            form = EmailForm(MultiDict({"email": ""}))
            self.assertFalse("None" in "%s" % form.email)
            self.assertTrue(form.validate())

            # Ensure required works

            class Email(db.Document):
                email = db.EmailField(required=True)

            EmailForm = model_form(Email)
            form = EmailForm(MultiDict({"email": ""}))
            self.assertFalse("None" in "%s" % form.email)
            self.assertFalse(form.validate())

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
                lead_paragraph = db.StringField(max_length=200)
                content = db.StringField(required=True)

            class LinkPost(BlogPost):
                url = db.StringField(required=True, max_length=200)
                interest = db.DecimalField(required=True)

            # Create a text-based post
            TextPostForm = model_form(
                TextPost,
                field_args={'lead_paragraph': {'textarea': True}})

            form = TextPostForm(MultiDict({
                'title': 'Using MongoEngine',
                'tags': ['mongodb', 'mongoengine']}))

            self.assertFalse(form.validate())

            form = TextPostForm(MultiDict({
                'title': 'Using MongoEngine',
                'content': 'See the tutorial',
                'tags': ['mongodb', 'mongoengine']}))

            self.assertTrue(form.validate())
            form.save()

            self.assertEqual(form.title.type, 'StringField')
            self.assertEqual(form.content.type, 'TextAreaField')
            self.assertEqual(form.lead_paragraph.type, 'TextAreaField')

            self.assertEquals(BlogPost.objects.first().title, 'Using MongoEngine')
            self.assertEquals(BlogPost.objects.count(), 1)

            form = TextPostForm(MultiDict({
                'title': 'Using Flask-MongoEngine',
                'content': 'See the tutorial',
                'tags': ['flask', 'mongodb', 'mongoengine']}))

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

            # Create a link post
            LinkPostForm = model_form(LinkPost)

            form = LinkPostForm(MultiDict({
                'title': 'Using Flask-MongoEngine',
                'url': 'http://flask-mongoengine.org',
                'interest': '0',
            }))
            form.validate()
            self.assertTrue(form.validate())

    def test_model_form_only(self):
        with self.app.test_request_context('/'):
            db = self.db

            class BlogPost(db.Document):
                title = db.StringField(required=True, max_length=200)
                posted = db.DateTimeField(default=datetime.datetime.now)
                tags = db.ListField(db.StringField())

            BlogPost.drop_collection()

            BlogPostForm = model_form(BlogPost, only=['tags'])
            form = BlogPostForm()
            self.assertTrue(hasattr(form, 'tags'))
            self.assertFalse(hasattr(form, 'posted'))

            BlogPostForm = model_form(BlogPost, exclude=['posted'])
            form = BlogPostForm()
            self.assertTrue(hasattr(form, 'tags'))
            self.assertFalse(hasattr(form, 'posted'))

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

            DogOwnerForm = model_form(DogOwner, field_args={
                'dog': {'allow_blank': True}
            })

            dog = Dog(name="fido")
            dog.save()

            form = DogOwnerForm(dog=dog)
            self.assertTrue(form.validate())

            self.assertEqual(wtforms.widgets.Select, type(form.dog.widget))
            self.assertFalse(form.dog.widget.multiple)

            # Validate the options - should contain a dog (selected) and a
            # blank option there should be an extra blank option.
            choices = list(form.dog)
            self.assertEqual(len(choices), 2)
            self.assertFalse(choices[0].checked)
            self.assertEqual(choices[0].data, '__None')
            self.assertTrue(choices[1].checked)
            self.assertEqual(choices[1].data, dog.pk)

            # Validate selecting one item
            form = DogOwnerForm(MultiDict({
                'dog': dog.id,
            }))
            self.assertEqual(form.dog.data, dog)

            # Validate selecting no item
            form = DogOwnerForm(MultiDict({
                'dog': u'__None',
            }), dog=dog)
            self.assertEqual(form.dog.data, None)

    def test_modelselectfield_multiple(self):
        with self.app.test_request_context('/'):
            db = self.db

            class Dog(db.Document):
                name = db.StringField()

            class DogOwner(db.Document):
                dogs = db.ListField(db.ReferenceField(Dog))

            DogOwnerForm = model_form(DogOwner, field_args={
                'dogs': {'allow_blank': True}
            })

            dogs = [Dog(name="fido"), Dog(name="rex")]
            for dog in dogs:
                dog.save()

            form = DogOwnerForm(dogs=dogs)
            self.assertTrue(form.validate())

            self.assertEqual(wtforms.widgets.Select, type(form.dogs.widget))
            self.assertTrue(form.dogs.widget.multiple)

            # Validate the options - both dogs should be selected and
            # there should be an extra blank option.
            choices = list(form.dogs)
            self.assertEqual(len(choices), 3)
            self.assertFalse(choices[0].checked)
            self.assertEqual(choices[0].data, '__None')
            self.assertTrue(choices[1].checked)
            self.assertEqual(choices[1].data, dogs[0].pk)
            self.assertTrue(choices[2].checked)
            self.assertEqual(choices[2].data, dogs[1].pk)

            # Validate selecting two items
            form = DogOwnerForm(MultiDict({
                'dogs': [dog.id for dog in dogs],
            }))
            self.assertEqual(form.dogs.data, dogs)

            # Validate selecting none actually empties the list
            form = DogOwnerForm(MultiDict({
                'dogs': '__None',
            }), dogs=dogs)
            self.assertEqual(form.dogs.data, None)

    def test_modelselectfield_multiple_initalvalue_None(self):
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

            form = DogOwnerForm(dogs=None)
            self.assertTrue(form.validate())

            self.assertEqual(wtforms.widgets.Select, type(form.dogs.widget))
            self.assertTrue(form.dogs.widget.multiple)

            # Validate if both dogs are selected
            choices = list(form.dogs)
            self.assertEqual(len(choices), 2)
            self.assertFalse(choices[0].checked)
            self.assertFalse(choices[1].checked)

    def test_modelradiofield(self):
        with self.app.test_request_context('/'):
            db = self.db

            choices = (('male', 'Male'), ('female', 'Female'), ('other', 'Other'))

            class Poll(db.Document):
                answer = db.StringField(choices=choices)

            PollForm = model_form(Poll, field_args={'answer': {'radio': True}})

            form = PollForm(answer=None)
            self.assertTrue(form.validate())

            self.assertEqual(form.answer.type, 'RadioField')
            self.assertEqual(form.answer.choices, choices)

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

            object_id = bson.ObjectId()
            Item(object_id, owner_item_id="1").save()

            try:
                Item(object_id, owner_item_id="1").save()
                self.fail("Should have raised duplicate key error")
            except:
                pass

            self.assertEqual(1, Item.objects.count())

    def test_sub_field_args(self):
        with self.app.test_request_context('/'):
            db = self.db

            class TestModel(db.Document):
                lst = db.ListField(db.StringField())

            field_args = {'lst': {'label': 'Custom Label',
                                  'field_args': {'widget': wtforms.widgets.HiddenInput(),
                                                 'label': "Hidden Input"}}}
            CustomForm = model_form(TestModel, field_args=field_args)

            custom_form = CustomForm(obj=TestModel(lst=["Foo"]))
            list_label = flask.render_template_string("{{ custom_form.lst.label }}", custom_form=custom_form)
            self.assertTrue("Custom Label" in list_label)
            self.assertTrue("Hidden Input" not in list_label)

            sub_label = flask.render_template_string("{{ custom_form.lst }}", custom_form=custom_form)
            self.assertTrue("Hidden Input" in sub_label)

    def test_modelselectfield_multiple_selected_elements_must_be_retained(self):
        with self.app.test_request_context('/'):
            db = self.db

            class Dog(db.Document):
                name = db.StringField()

                def __unicode__(self):
                    return self.name

            class DogOwner(db.Document):
                dogs = db.ListField(db.ReferenceField(Dog))

            DogOwnerForm = model_form(DogOwner)

            fido = Dog(name="fido").save()
            Dog(name="rex").save()

            dogOwner = DogOwner(dogs=[fido])
            form = DogOwnerForm(obj=dogOwner)
            html = form.dogs()

            m = re.search("<option selected .+?>(.*?)</option>", html)
            self.assertTrue(m is not None, "Should have one selected option")
            self.assertEqual("fido", m.group(1))

    def test_model_form_help_text(self):
        with self.app.test_request_context('/'):
            db = self.db

            class BlogPost(db.Document):
                title = db.StringField(required=True, help_text="Some imaginative title to set the world on fire")

            post = BlogPost(title="hello world").save()

            BlogPostForm = model_form(BlogPost)
            form = BlogPostForm(instance=post)

            self.assertEqual(form.title.description, "Some imaginative title to set the world on fire")

    def test_shared_field_args(self):
        with self.app.test_request_context('/'):
            db = self.db

            class BlogPost(db.Document):
                title = db.StringField(required=True)
                content = db.StringField(required=False)

            shared_field_args = {'title': {'validators': [
                wtforms.validators.Regexp('test')
            ]}}

            TitleOnlyForm = model_form(BlogPost, field_args=shared_field_args,
                                       exclude=['content'])
            BlogPostForm = model_form(BlogPost, field_args=shared_field_args)

            # ensure shared field_args don't create duplicate validators
            title_only_form = TitleOnlyForm()
            self.assertEqual(len(title_only_form.title.validators), 2)

            blog_post_form = BlogPostForm()
            self.assertEqual(len(blog_post_form.title.validators), 2)

    def test_embedded_model_form(self):
        with self.app.test_request_context('/'):
            db = self.db

            class Content(db.EmbeddedDocument):
                text = db.StringField()
                lang = db.StringField(max_length=3)

            class Post(db.Document):
                title = db.StringField(max_length=120, required=True)
                tags = db.ListField(db.StringField(max_length=30))
                content = db.EmbeddedDocumentField("Content")

            PostForm = model_form(Post)
            form = PostForm()
            self.assertTrue("content-text" in "%s" % form.content.text)


if __name__ == '__main__':
    unittest.main()

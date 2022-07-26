import datetime
import re

import bson
import flask
import pytest
from mongoengine import NotUniqueError, queryset_manager
from werkzeug.datastructures import MultiDict

try:
    from flask_mongoengine.wtf.orm import model_form
except ImportError:
    model_form = None
wtforms = pytest.importorskip("wtforms")


def test_binaryfield(app, db):

    with app.test_request_context("/"):

        class Binary(db.Document):
            binary = db.BinaryField()

        BinaryForm = model_form(Binary)
        form = BinaryForm(MultiDict({"binary": "1"}))
        assert form.validate()
        form.save()


def test_choices_coerce(app, db):

    with app.test_request_context("/"):

        CHOICES = ((1, "blue"), (2, "red"))

        class MyChoices(db.Document):
            pill = db.IntField(choices=CHOICES)

        MyChoicesForm = model_form(MyChoices)
        form = MyChoicesForm(MultiDict({"pill": "1"}))
        assert form.validate()
        form.save()
        assert MyChoices.objects.first().pill == 1


def test_list_choices_coerce(app, db):

    with app.test_request_context("/"):

        CHOICES = ((1, "blue"), (2, "red"))

        class MyChoices(db.Document):
            pill = db.ListField(field=db.IntField(choices=CHOICES))

        MyChoicesForm = model_form(MyChoices)
        form = MyChoicesForm(MultiDict({"pill": "1"}))
        assert form.validate()
        form.save()
        assert MyChoices.objects.first().pill[0] == 1


def test_emailfield(app, db):

    with app.test_request_context("/"):

        class Email(db.Document):
            email = db.EmailField(required=False)

        EmailForm = model_form(Email)
        form = EmailForm(instance=Email())
        assert "None" not in f"{form.email}"
        assert form.validate()

        form = EmailForm(MultiDict({"email": ""}))
        assert "None" not in f"{form.email}"
        assert form.validate()

        class Email(db.Document):
            email = db.EmailField(required=True)

        EmailForm = model_form(Email)
        form = EmailForm(MultiDict({"email": ""}))
        assert "None" not in f"{form.email}"
        assert not form.validate()


def test_model_form(app, db):
    with app.test_request_context("/"):

        class BlogPost(db.Document):
            meta = {"allow_inheritance": True}
            title = db.StringField(required=True, max_length=200)
            posted = db.DateTimeField(default=datetime.datetime.now)
            tags = db.ListField(field=db.StringField())

        class TextPost(BlogPost):
            email = db.EmailField(required=False)
            lead_paragraph = db.StringField(max_length=200)
            content = db.StringField(required=True)

        class LinkPost(BlogPost):
            url = db.StringField(required=True, max_length=200)
            interest = db.DecimalField(required=True)

        # Create a text-based post
        TextPostForm = model_form(
            TextPost, field_args={"lead_paragraph": {"textarea": True}}
        )

        form = TextPostForm(
            MultiDict(
                {"title": "Using MongoEngine", "tags": ["mongodb", "mongoengine"]}
            )
        )

        assert not form.validate()

        form = TextPostForm(
            MultiDict(
                {
                    "title": "Using MongoEngine",
                    "content": "See the tutorial",
                    "tags": ["mongodb", "mongoengine"],
                }
            )
        )

        assert form.validate()
        form.save()

        assert form.title.type == "StringField"
        assert form.content.type == "TextAreaField"
        assert form.lead_paragraph.type == "TextAreaField"

        assert BlogPost.objects.first().title == "Using MongoEngine"
        assert BlogPost.objects.count() == 1

        form = TextPostForm(
            MultiDict(
                {
                    "title": "Using Flask-MongoEngine",
                    "content": "See the tutorial",
                    "tags": ["flask", "mongodb", "mongoengine"],
                }
            )
        )

        assert form.validate()
        form.save()
        assert BlogPost.objects.count() == 2

        post = BlogPost.objects(title="Using Flask-MongoEngine").get()

        form = TextPostForm(
            MultiDict(
                {
                    "title": "Using Flask-MongoEngine",
                    "content": "See the tutorial",
                    "tags-0": "flask",
                    "tags-1": "mongodb",
                    "tags-2": "mongoengine",
                    "tags-3": "flask-mongoengine",
                }
            ),
            instance=post,
        )
        assert form.validate()
        form.save()
        post = post.reload()

        assert post.tags == ["flask", "mongodb", "mongoengine", "flask-mongoengine"]

        # Create a link post
        LinkPostForm = model_form(LinkPost)

        form = LinkPostForm(
            MultiDict(
                {
                    "title": "Using Flask-MongoEngine",
                    "url": "http://flask-mongoengine.org",
                    "interest": "0",
                }
            )
        )
        form.validate()
        assert form.validate()


def test_model_form_only(app, db):
    with app.test_request_context("/"):

        class BlogPost(db.Document):
            title = db.StringField(required=True, max_length=200)
            posted = db.DateTimeField(default=datetime.datetime.now)
            tags = db.ListField(field=db.StringField())

        BlogPost.drop_collection()

        BlogPostForm = model_form(BlogPost, only=["tags"])
        form = BlogPostForm()
        assert hasattr(form, "tags")
        assert not hasattr(form, "posted")

        BlogPostForm = model_form(BlogPost, exclude=["posted"])
        form = BlogPostForm()
        assert hasattr(form, "tags")
        assert not hasattr(form, "posted")


def test_model_form_with_custom_query_set(app, db):
    with app.test_request_context("/"):

        class Dog(db.Document):
            breed = db.StringField()

            @queryset_manager
            def large_objects(cls, queryset):
                return queryset(breed__in=["german sheppard", "wolfhound"])

        class DogOwner(db.Document):
            dog = db.ReferenceField(document_type=Dog)

        big_dogs = [Dog(breed="german sheppard"), Dog(breed="wolfhound")]
        dogs = [Dog(breed="poodle")] + big_dogs
        for dog in dogs:
            dog.save()

        BigDogForm = model_form(
            DogOwner, field_args={"dog": {"queryset": Dog.large_objects}}
        )

        form = BigDogForm(dog=big_dogs[0])
        assert form.validate()
        assert big_dogs == [d[1] for d in form.dog.iter_choices()]


def test_modelselectfield(app, db):
    with app.test_request_context("/"):

        class Dog(db.Document):
            name = db.StringField()

        class DogOwner(db.Document):
            dog = db.ReferenceField(document_type=Dog)

        DogOwnerForm = model_form(DogOwner, field_args={"dog": {"allow_blank": True}})

        dog = Dog(name="fido")
        dog.save()

        form = DogOwnerForm(dog=dog)
        assert form.validate()

        assert isinstance(form.dog.widget, wtforms.widgets.Select)
        assert not form.dog.widget.multiple

        # Validate the options - should contain a dog (selected) and a
        # blank option there should be an extra blank option.
        choices = list(form.dog)
        assert len(choices) == 2
        assert not choices[0].checked
        assert choices[0].data == "__None"
        assert choices[1].checked
        assert choices[1].data == dog.pk

        # Validate selecting one item
        form = DogOwnerForm(MultiDict({"dog": dog.id}))
        assert form.dog.data == dog

        # Validate selecting no item
        form = DogOwnerForm(MultiDict({"dog": "__None"}), dog=dog)
        assert form.dog.data is None


def test_modelselectfield_multiple(app, db):
    with app.test_request_context("/"):

        class Dog(db.Document):
            name = db.StringField()

        class DogOwner(db.Document):
            dogs = db.ListField(field=db.ReferenceField(document_type=Dog))

        DogOwnerForm = model_form(DogOwner, field_args={"dogs": {"allow_blank": True}})

        dogs = [Dog(name="fido"), Dog(name="rex")]
        for dog in dogs:
            dog.save()

        form = DogOwnerForm(dogs=dogs)
        assert form.validate()

        assert isinstance(form.dogs.widget, wtforms.widgets.Select)
        assert form.dogs.widget.multiple

        # Validate the options - both dogs should be selected and
        # there should be an extra blank option.
        choices = list(form.dogs)
        assert len(choices) == 3
        assert not choices[0].checked
        assert choices[0].data == "__None"
        assert choices[1].checked
        assert choices[1].data == dogs[0].pk
        assert choices[2].checked
        assert choices[2].data == dogs[1].pk

        # Validate selecting two items
        form = DogOwnerForm(MultiDict({"dogs": [dog.id for dog in dogs]}))
        assert form.dogs.data == dogs

        # Validate selecting none actually empties the list
        form = DogOwnerForm(MultiDict({"dogs": "__None"}), dogs=dogs)
        assert form.dogs.data is None


def test_modelselectfield_multiple_initalvalue_None(app, db):
    with app.test_request_context("/"):

        class Dog(db.Document):
            name = db.StringField()

        class DogOwner(db.Document):
            dogs = db.ListField(field=db.ReferenceField(document_type=Dog))

        DogOwnerForm = model_form(DogOwner)

        dogs = [Dog(name="fido"), Dog(name="rex")]
        for dog in dogs:
            dog.save()

        form = DogOwnerForm(dogs=None)
        assert form.validate()

        assert isinstance(form.dogs.widget, wtforms.widgets.Select)
        assert form.dogs.widget.multiple

        # Validate if both dogs are selected
        choices = list(form.dogs)
        assert len(choices) == 2
        assert not choices[0].checked
        assert not choices[1].checked


def test_modelradiofield(app, db):
    with app.test_request_context("/"):

        choices = [("male", "Male"), ("female", "Female"), ("other", "Other")]

        class Poll(db.Document):
            answer = db.StringField(choices=choices)

        PollForm = model_form(Poll, field_args={"answer": {"radio": True}})

        form = PollForm(answer=None)
        assert form.validate()

        assert form.answer.type == "RadioField"
        assert form.answer.choices == choices


def test_filefield(app, db):
    with app.test_request_context("/"):

        class FileUpload(db.Document):
            file = db.FileField()

        FileUploadForm = model_form(FileUpload)

        form = FileUploadForm(file=None)

        assert isinstance(form.file.widget, wtforms.widgets.FileInput)


def test_passwordfield(app, db):
    with app.test_request_context("/"):

        class User(db.Document):
            password = db.StringField()

        UserForm = model_form(User, field_args={"password": {"password": True}})
        form = UserForm(password="12345")
        assert isinstance(form.password.widget, wtforms.widgets.PasswordInput)


def test_unique_with(app, db):

    with app.test_request_context("/"):

        class Item(db.Document):
            owner_id = db.ObjectIdField(required=True)
            owner_item_id = db.StringField(required=True, unique_with="owner_id")

        Item.drop_collection()

        object_id = bson.ObjectId()
        Item(owner_id=object_id, owner_item_id="1").save()

        with pytest.raises(NotUniqueError):
            Item(owner_id=object_id, owner_item_id="1").save()

        assert 1 == Item.objects.count()


def test_sub_field_args(app, db):
    with app.test_request_context("/"):

        class TestModel(db.Document):
            lst = db.ListField(field=db.StringField())

        field_args = {
            "lst": {
                "label": "Custom Label",
                "field_args": {
                    "widget": wtforms.widgets.HiddenInput(),
                    "label": "Hidden Input",
                },
            }
        }
        CustomForm = model_form(TestModel, field_args=field_args)

        custom_form = CustomForm(obj=TestModel(lst=["Foo"]))
        list_label = flask.render_template_string(
            "{{ custom_form.lst.label }}", custom_form=custom_form
        )
        assert "Custom Label" in list_label
        assert "Hidden Input" not in list_label

        sub_label = flask.render_template_string(
            "{{ custom_form.lst }}", custom_form=custom_form
        )
        assert "Hidden Input" in sub_label


def test_modelselectfield_multiple_selected_elements_must_be_retained(app, db):
    with app.test_request_context("/"):

        class Dog(db.Document):
            name = db.StringField()

            def __unicode__(self):
                return self.name

        class DogOwner(db.Document):
            dogs = db.ListField(field=db.ReferenceField(document_type=Dog))

        DogOwnerForm = model_form(DogOwner)

        fido = Dog(name="fido").save()
        Dog(name="rex").save()

        dogOwner = DogOwner(dogs=[fido])
        form = DogOwnerForm(obj=dogOwner)
        html = form.dogs()

        m = re.search("<option selected .+?>(.*?)</option>", html)

        # Should have one selected option
        assert m is not None
        assert "fido" == m.group(1)


def test_model_form_help_text(app, db):
    with app.test_request_context("/"):

        class BlogPost(db.Document):
            title = db.StringField(
                required=True,
                help_text="Some imaginative title to set the world on fire",
            )

        post = BlogPost(title="hello world").save()

        BlogPostForm = model_form(BlogPost)
        form = BlogPostForm(instance=post)

        assert (
            form.title.description == "Some imaginative title to set the world on fire"
        )


def test_shared_field_args(app, db):
    with app.test_request_context("/"):

        class BlogPost(db.Document):
            title = db.StringField(required=True)
            content = db.StringField(required=False)

        shared_field_args = {
            "title": {"validators": [wtforms.validators.Regexp("test")]}
        }

        TitleOnlyForm = model_form(
            BlogPost, field_args=shared_field_args, exclude=["content"]
        )
        BlogPostForm = model_form(BlogPost, field_args=shared_field_args)

        # ensure shared field_args don't create duplicate validators
        title_only_form = TitleOnlyForm()
        assert len(title_only_form.title.validators) == 2

        blog_post_form = BlogPostForm()
        assert len(blog_post_form.title.validators) == 2


def test_embedded_model_form(app, db):
    with app.test_request_context("/"):

        class Content(db.EmbeddedDocument):
            text = db.StringField()
            lang = db.StringField(max_length=3)

        class Post(db.Document):
            title = db.StringField(max_length=120, required=True)
            tags = db.ListField(field=db.StringField(max_length=30))
            content = db.EmbeddedDocumentField(document_type="Content")

        PostForm = model_form(Post)
        form = PostForm()
        assert "content-text" in "%s" % form.content.text


def test_form_label_modifier(app, db):
    with app.test_request_context("/"):

        class FoodItem(db.Document):
            title = db.StringField()

        class FoodStore(db.Document):
            title = db.StringField(max_length=120, required=True)
            food_items = db.ListField(field=db.ReferenceField(document_type=FoodItem))

            def food_items_label_modifier(obj):
                return obj.title

        fruit_names = ["banana", "apple", "pear"]

        food_items = [FoodItem(title=name).save() for name in fruit_names]

        FoodStore(title="John's fruits", food_items=food_items).save()

        FoodStoreForm = model_form(FoodStore)
        form = FoodStoreForm()

        assert [obj.label.text for obj in form.food_items] == fruit_names


def test_csrf_token(app, db):
    # fixes MongoEngine/flask-mongoengine#436
    app.config["WTF_CSRF_ENABLED"] = True
    with app.test_request_context("/"):

        class DummyCSRF(wtforms.csrf.core.CSRF):
            def generate_csrf_token(self, csrf_token_field):
                return "dummytoken"

        class MyModel(db.Document):
            pass

        form = model_form(MyModel)(
            MultiDict({"csrf_token": "dummytoken"}), meta={"csrf_class": DummyCSRF}
        )
        assert "csrf_token" in form
        assert form.validate()
        form.save()

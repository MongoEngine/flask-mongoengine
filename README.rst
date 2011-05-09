Flask-MongoEngine
=================

A Flask extension that provides integration with `MongoEngine <http://hmarr.com/mongoengine/>`_. It handles connection management for your app.

You can also use `WTForms <http://wtforms.simplecodes.com/>`_ as model forms for your models.


Configuration
=============

Basic setup is easy, just fetch the extension::

    from flask import Flask
    from flaskext.mongoengine import MongoEngine

    app = Flask(__name__)
    app.config.from_pyfile('the-config.cfg')
    db = MongoEngine(app)


MongoEngine and WTForms
=======================

You can use MongoEngine and WTForms like so::

    from flaskext.mongoengine.wtforms import model_form

    class User(db.Document):
        email = db.StringField(required=True)
        first_name = db.StringField(max_length=50)
        last_name = db.StringField(max_length=50)

    class Content(db.EmbeddedDocument):
        text = db.StringField()
        lang = db.StringField(max_length=3)

    class Post(Document):
        title = db.StringField(max_length=120, required=True)
        author = db.ReferenceField(User)
        tags = db.ListField(StringField(max_length=30))
        content = db.EmbeddedDocumentField(Content)

    PostForm = model_form(Post)

    def add_post(request):
        form = PostForm(request.POST)
        if request.method == 'POST' and form.validate():
            # do something
            redirect('done')
        return render_response('add_post.html', form=form)


Supported fields
-----------------

* StringField
* BinaryField
* URLField
* EmailField
* IntField
* FloatField
* DecimalField
* BooleanField
* DateTimeField
* **ListField** (using wtforms.fields.FieldList ) 
* SortedListField (duplicate ListField)
* **EmbeddedDocumentField** (using wtforms.fields.FormField and generating inline Form)
* **ReferenceField** (using wtforms.fields.SelectFieldBase with options loaded from QuerySet or Document)
* DictField

Not currently supported field types:
-----------------------------------

* ObjectIdField
* GeoLocationField
* GenericReferenceField


Credits
========

Inspired by two repos:

`danjac <https://bitbucket.org/danjac/flask-mongoengine>`_
`maratfm <https://bitbucket.org/maratfm/wtforms>`_

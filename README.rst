Flask-MongoEngine
=================

A Flask extension that provides integration with `MongoEngine <http://hmarr.com/mongoengine/>`_. It handles connection management for your app.

You can also use `WTForms <http://wtforms.simplecodes.com/>`_ as model forms for your models.

Installing Flask-MongoEngine
============================

Install with **pip**::

    pip install https://github.com/sbook/flask-mongoengine/tarball/master


Configuration
=============

Basic setup is easy, just fetch the extension::

    from flask import Flask
    from flaskext.mongoengine import MongoEngine

    app = Flask(__name__)
    app.config.from_pyfile('the-config.cfg')
    db = MongoEngine(app)


Custom Queryset
===============

To get `get_or_404`, `first_or_404` or `paginate` you need to declare the queryset in your model meta like so::

    class Todo(db.Document):
        title = db.StringField(max_length=60)
        text = db.StringField()
        done = db.BooleanField(default=False)
        pub_date = db.DateTimeField(default=datetime.datetime.now)
        
        meta = dict(queryset_class=db.QuerySet)

The you can do things like::

    # 404 if not exists
    def view_todo(todo_id):
        todo = Todo.objects.get_or_404(_id=todo_id)
    ..
    
    # Paginate through todo
    def view_todos(page=1):
        page = Todo.objects.paginate(page=page, per_page=10)


In the template::

    {% macro render_pagination(pagination, endpoint) %}
      <div class=pagination>
      {%- for page in pagination.iter_pages() %}
        {% if page %}
          {% if page != pagination.page %}
            <a href="{{ url_for(endpoint, page=page) }}">{{ page }}</a>
          {% else %}
            <strong>{{ page }}</strong>
          {% endif %}
        {% else %}
          <span class=ellipsis>…</span>
        {% endif %}
      {%- endfor %}
      </div>
    {% endmacro %}


MongoEngine and WTForms
=======================

You can use MongoEngine and WTForms like so::

    from flaskext.mongoengine.wtf import model_form

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

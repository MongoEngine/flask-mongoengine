Flask-MongoEngine
=================

A Flask extension that provides integration with `MongoEngine <http://mongoengine.org/>`_. It handles connection management for your app.

You can also use `WTForms <http://wtforms.simplecodes.com/>`_ as model forms for your models.

Installing Flask-MongoEngine
============================

Install with **pip**::

    pip install flask-mongoengine

Configuration
=============

Basic setup is easy, just fetch the extension::

    from flask import Flask
    from flask.ext.mongoengine import MongoEngine

    app = Flask(__name__)
    app.config.from_pyfile('the-config.cfg')
    db = MongoEngine(app)


Custom Queryset
===============

flask-mongoengine attaches the following methods to Mongoengine's default QuerySet:

* **get_or_404**: works like .get(), but calls abort(404) if the object DoesNotExist.
* **first_or_404**: same as above, except for .first().
* **paginate**: paginates the QuerySet. Takes two arguments, *page* and *per_page*.
* **paginate_field**: paginates a field from one document in the QuerySet.
  Arguments: *field_name*, *doc_id*, *page*, *per_page*.

Examples::

    # 404 if object doesn't exist
    def view_todo(todo_id):
        todo = Todo.objects.get_or_404(_id=todo_id)
    ..

    # Paginate through todo
    def view_todos(page=1):
        paginated_todos = Todo.objects.paginate(page=page, per_page=10)

    # Paginate through tags of todo
    def view_todo_tags(page=1):
        todo_id = Todo.objects.first().id
        paginated_tags = Todo.objects.paginate_field('tags', todo_id, page,
                                                     per_page=10)

Properties of the pagination object include: iter_pages, next, prev, has_next,
has_prev, next_num, prev_num.

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

    from flask.ext.mongoengine.wtf import model_form

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
================

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
====================================

* ObjectIdField
* GeoLocationField
* GenericReferenceField

Debug Toolbar Panel
===================

.. image:: _static/debugtoolbar.png
  :target: #debug-toolbar-panel

If you use the Flask-DebugToolbar you can add
`'flask.ext.mongoengine.panels.MongoDebugPanel'` to the `DEBUG_TB_PANELS` config
list and then it will automatically track your queries.


Credits
========

Inspired by two repos:

`danjac <https://bitbucket.org/danjac/flask-mongoengine>`_
`maratfm <https://bitbucket.org/maratfm/wtforms>`_
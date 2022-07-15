# MongoEngine and WTForms

flask-mongoengine automatically generates WTForms from MongoEngine models:

```python
from flask_mongoengine.wtf import model_form

class User(db.Document):
    email = db.StringField(required=True)
    first_name = db.StringField(max_length=50)
    last_name = db.StringField(max_length=50)

class Content(db.EmbeddedDocument):
    text = db.StringField()
    lang = db.StringField(max_length=3)

class Post(db.Document):
    title = db.StringField(max_length=120, required=True, validators=[validators.InputRequired(message='Missing title.'),])
    author = db.ReferenceField(User)
    tags = db.ListField(db.StringField(max_length=30))
    content = db.EmbeddedDocumentField(Content)

PostForm = model_form(Post)

def add_post(request):
    form = PostForm(request.POST)
    if request.method == 'POST' and form.validate():
        # do something
        redirect('done')
    return render_template('add_post.html', form=form)
```

For each MongoEngine field, the most appropriate WTForm field is used.
Parameters allow the user to provide hints if the conversion is not implicit::

```python
PostForm = model_form(Post, field_args={'title': {'textarea': True}})
```

Supported parameters:

For fields with `choices`:

- `multiple` to use a SelectMultipleField
- `radio` to use a RadioField

For ``StringField``:

- `password` to use a PasswordField
- `textarea` to use a TextAreaField

For ``ListField``:

- `min_entries` to set the minimal number of entries

(By default, a StringField is converted into a TextAreaField if and only if it has no
max_length.)

## Supported fields

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
* **ReferenceField** (using wtforms.fields.SelectFieldBase with options loaded from
  QuerySet or Document)
* DictField

## Not currently supported field types:

* ObjectIdField
* GeoLocationField
* GenericReferenceField

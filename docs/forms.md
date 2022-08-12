# WTForms integration

```{important}
Documentation below is related to project version 2.0.0 or higher, old versions has
completely different approach for forms generation.

And despite the fact that the old code is included in version 2.0.0 to keep correct
deprecation workflow (where possible), it is not documented (and was not) and not
maintained.

If you faced any forms problems, consider migration to new methods and approach.
```

Flask-Mongoengine and Flask-WTF/WTForms are heavily integrated, to reduce amount of
boilerplate code, required to make database model and online form. In the same time
a lot of options was created to keep extreme flexibility.

After database model definition user does not require to repeat same code in form
definition, instead it is possible to use integrated converter, that will do most of
the work.

Flask-Mongoengine will transform some model's properties to Flask-WTF/WTForms
validators, so user does not need to care about standards. For full list of
transformations, please review [global transforms] and specific field documentation
below.

In the same time, user is able to adjust database fields definition with
specific settings as on stage of Document model definition, as on form generation stage.
This allows to create several forms for same model, for different circumstances.

## Requirements

For correct integration behavior several requirements should be met:

- Document classes should be used from Flask-Mongoengine
  {class}`flask_mongoengine.MongoEngine` class, or from
  {mod}`flask_mongoengine.documents` module.
- Document classes should be used from Flask-Mongoengine
  {class}`flask_mongoengine.MongoEngine` class, or from
  {mod}`flask_mongoengine.db_fields` module.

## Global transforms

For all fields, processed by Flask-Mongoengine integration:

- If model field definition have {attr}`wtf_validators` defined, they will be
  forwarded to WTForm as {attr}`validators`. This is not protection from
  {attr}`validators` extension by Flask-Mongoengine.
- If model field definition have {attr}`wtf_filters` defined, they will be forwarded to
  WTForm as {attr}`filters`.
- If model field definition have {attr}`required`, then
  {class}`~wtforms.validators.InputRequired`
  will be added to form {attr}`validators`, otherwise
  {class}`~wtforms.validators.Optional`
  added.
- If model field definition have {attr}`verbose_name` it will be used as form field
  {attr}`label`, otherwise pure field name used.
- If model field definition have {attr}`help_text` it will be used as form field
  {attr}`description`, otherwise empty string used.
- Field's {attr}`default` used as form {attr}`default`, that's why special WTForms
  fields implementations was created. Details can be found in
  {mod}`flask_mongoengine.wtf.fields` module. In new form generator only 'Mongo'
  prefixed classes are used for fields, other classes are deprecated and will be
  removed in version **3.0.0**. If you have own nesting classes, you should check
  inheritance and make an update.
- Field's {attr}`choices`, if exist, used as form {attr}`choices`.

```{warning}
As at version **2.0.0** there is no {attr}`wtf_validators` duplicates/conflicts check.
User should be careful with manual {attr}`wtf_validators` setup. And in case of forms
problems this is first place to look on.

{attr}`wtf_validators` and {attr}`wtf_filters` duplication check expected in future
versions; PRs are welcome.
```

Some additional transformations are made by specific field, check exact field
documentation below for more info.

## Supported fields

### BinaryField

Not yet documented. Please help us with new pull request.

### BooleanField

Not yet documented. Please help us with new pull request.

### DateField

Not yet documented. Please help us with new pull request.

### DateTimeField

Not yet documented. Please help us with new pull request.

### DecimalField

- API: {class}`.db_fields.DecimalField`
- Default form field class: {class}`wtforms.fields.DecimalField`

#### Form generation behaviour

From form generation side this field is pretty standard and do not use any form
generation adjustments.

If database field definition has any of {attr}`min_value` or {attr}`max_value`, then
{class}`~wtforms.validators.NumberRange` validator will be added to form field.

#### Examples

numbers_demo.py in example app contain basic non-requirement example. You can adjust
it to any provided example for test purposes.

##### Not limited DecimalField

```python
"""numbers_demo.py"""
from example_app.models import db


class NumbersDemoModel(db.Document):
    """Documentation example model."""

    decimal_field_unlimited = db.DecimalField()
```

##### Limited DecimalField

```python
"""numbers_demo.py"""
from decimal import Decimal

from example_app.models import db


class NumbersDemoModel(db.Document):
    """Documentation example model."""

    decimal_field_limited = db.DecimalField(
        min_value=Decimal("1"), max_value=Decimal("200.455")
    )
```

### DictField

Not yet documented. Please help us with new pull request.

### EmailField

- API: {class}`.db_fields.EmailField`
- Default form field class: {class}`~.MongoEmailField`

#### Form generation behaviour

Unlike [StringField] WTForm class of the field is not adjusted by normal form
generation sequence and always match {class}`~.MongoEmailField`. All other
adjustments, related to validators insert are work with EmailField in the same way,
as in [StringField].

Additional {class}`~wtforms.validators.Email` validator is also inserted to form
field, to exclude unnecessary database request, if form data incorrect.

Field respect user's adjustments in {attr}`wtf_field_class` option of
{class}`.db_fields.EmailField`. This will change form field display, but will not
change inserted validators.

#### Examples

strings_demo.py in example app contain basic non-requirement example. You can adjust
it to any provided example for test purposes.

##### Not required EmailField

```python
"""strings_demo.py"""
from example_app.models import db


class StringsDemoModel(db.Document):
    """Documentation example model."""

    url_field = db.EmailField()
````

##### Required EmailField

```python
"""strings_demo.py"""
from example_app.models import db


class StringsDemoModel(db.Document):
    """Documentation example model."""

    required_url_field = db.EmailField(required=True)
````

### EmbeddedDocumentField

Not yet documented. Please help us with new pull request.

### FileField

Not yet documented. Please help us with new pull request.

### FloatField

```{versionchanged} 2.0.0
Default form field class changed from: {class}`wtforms.fields.FloatField` to
{class}`~.fields.MongoFloatField`.
```

- API: {class}`.db_fields.FloatField`
- Default form field class: {class}`~.fields.MongoFloatField`

#### Form generation behaviour

For Mongo database {class}`~.db_fields.FloatField` special WTForm field was created.
This field's behaviour is the same, as for {class}`wtforms.fields.FloatField`,
but the widget is replaced to {class}`~wtforms.widgets.NumberInput`, this should make a
look of generated form better. It is possible, that in some cases usage of base,
{class}`wtforms.fields.FloatField` can be required by form design. Both fields are
completely compatible, and replace can be done with {attr}`wtf_field_class` db form
parameter.

If database field definition has any of {attr}`min_value` or {attr}`max_value`, then
{class}`~wtforms.validators.NumberRange` validator will be added to form field.

#### Examples

numbers_demo.py in example app contain basic non-requirement example. You can adjust
it to any provided example for test purposes.

##### Not limited FloatField

```python
"""numbers_demo.py"""
from example_app.models import db


class NumbersDemoModel(db.Document):
    """Documentation example model."""

    float_field_unlimited = db.FloatField()
```

##### Limited FloatField

```python
"""numbers_demo.py"""
from example_app.models import db


class NumbersDemoModel(db.Document):
    """Documentation example model."""

    float_field_limited = db.FloatField(min_value=float(1), max_value=200.455)
```

### IntField

- API: {class}`.db_fields.IntField`
- Default form field class: {class}`wtforms.fields.IntegerField`

#### Form generation behaviour

From form generation side this field is pretty standard and do not use any form
generation adjustments.

If database field definition has any of {attr}`min_value` or {attr}`max_value`, then
{class}`~wtforms.validators.NumberRange` validator will be added to form field.

#### Examples

numbers_demo.py in example app contain basic non-requirement example. You can adjust
it to any provided example for test purposes.

##### Not limited IntField

```python
"""numbers_demo.py"""
from example_app.models import db


class NumbersDemoModel(db.Document):
    """Documentation example model."""

    integer_field_unlimited = db.IntField()
```

##### Limited IntField

```python
"""numbers_demo.py"""
from example_app.models import db


class NumbersDemoModel(db.Document):
    """Documentation example model."""

    integer_field_limited = db.IntField(min_value=1, max_value=200)
```

### ListField

Not yet documented. Please help us with new pull request.

### ReferenceField

Not yet documented. Please help us with new pull request.

### SortedListField (partly?)

Not yet documented. Please help us with new pull request.

### StringField

- API: {class}`.db_fields.StringField`
- Default form field class: Selected by field settings combination

#### Form generation behaviour

By default, during WTForm generation for fields without specified size (
{attr}`min_length` or {attr}`max_length`) class {class}`.MongoTextAreaField` is used,
in case when {attr}`min_length` or {attr}`max_length` set, then
{class}`.MongoStringField` used and {class}`~wtforms.validators.Length` will be added
to form field validators. This allows to keep documents of any size in mongodb.

In some cases class {class}`~.MongoStringField` is not the best choice for field, even
with limited size. In this case user can easily overwrite generated field class by
providing {attr}`wtf_field_class` on {class}`.db_fields.StringField` field declaration,
as on document, as well as on form generation steps.

If database field definition has {attr}`regex` parameter set, then
{class}`~wtforms.validators.Regexp` validator will be added to the form field.

#### Features deprecated

Field declaration step keyword arguments {attr}`password` and {attr}`textarea` are
deprecated in Flask-Mongoengine version **2.0.0** and exist only to make migration
steps easy.

To implement same behaviour, user should use {attr}`wtf_field_class` setting on
{class}`.db_fields.StringField` init.

#### Related WTForm custom fields

Several special WTForms field implementation was created to support mongodb database
behaviour and do not create any values in database, in case of empty fields. They
can be used as {attr}`wtf_field_class` setting or independently. Some of them used
in another database fields too, but all of them based on
{class}`wtforms.fields.StringField` and {class}`~.EmptyStringIsNoneMixin`. You can use
{class}`~.EmptyStringIsNoneMixin` for own field types.

- {class}`~.MongoEmailField`
- {class}`~.MongoHiddenField`
- {class}`~.MongoPasswordField`
- {class}`~.MongoSearchField`
- {class}`~.MongoStringField`
- {class}`~.MongoTelField`
- {class}`~.MongoTextAreaField`
- {class}`~.MongoURLField`

#### Examples

strings_demo.py in example app contain basic non-requirement example. You can adjust
it to any provided example for test purposes.

##### Not limited StringField as MongoTextAreaField

```python
"""strings_demo.py"""
from example_app.models import db


class StringsDemoModel(db.Document):
    """Documentation example model."""

    string_field = db.StringField()
```

##### Not limited StringField as MongoTelField

```python
"""strings_demo.py"""
from example_app.models import db
from flask_mongoengine.wtf import fields as mongo_fields


class StringsDemoModel(db.Document):
    """Documentation example model."""

    tel_field = db.StringField(wtf_field_class=mongo_fields.MongoTelField)
```

##### Not limited StringField as MongoTextAreaField with https regex

[mongoengine] and [wtforms] projects are not consistent in how they work with regex.
You will be safe, if you use {func}`re.compile` each time, when you work with regex
settings, before parent projects itself.

```python
"""strings_demo.py"""
import re

from example_app.models import db


class StringsDemoModel(db.Document):
    """Documentation example model."""

    regexp_string_field = db.StringField(regex=re.compile(
        r"^(https:\/\/)[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+,;=]+$"
    ))
```

##### Size limited StringField as MongoStringField

```python
"""strings_demo.py"""
from example_app.models import db


class StringsDemoModel(db.Document):
    """Documentation example model."""

    sized_string_field = db.StringField(min_length=5)
```

##### Required password field with minimum size

```python
"""strings_demo.py"""
from example_app.models import db
from flask_mongoengine.wtf import fields as mongo_fields


class StringsDemoModel(db.Document):
    """Documentation example model."""

    password_field = db.StringField(
        wtf_field_class=mongo_fields.MongoPasswordField,
        required=True,
        min_length=5,
    )
```

### URLField

- API: {class}`.db_fields.URLField`
- Default form field class: {class}`~.MongoURLField`

#### Form generation behaviour

Unlike [StringField] WTForm class of the field is not adjusted by normal form
generation sequence and always match {class}`~.MongoURLField`. All other
adjustments, related to validators insert are work with EmailField in the same way,
as in [StringField].

Additional {class}`~wtforms.validators.Regexp` validator is also inserted to form
field, to exclude unnecessary database request, if form data incorrect. This
validator use regexp, provided in {attr}`url_regex` of {class}`.db_fields.URLField`,
or default URL regexp from [mongoengine] project. This is different from
Flask-Mongoengine version **1.0.0** or earlier, where {class}`~wtforms.validators.URL`
was inserted. This was changed, to exclude validators conflicts.

```{important}
{func}`~.model_form` is still use {class}`~wtforms.validators.URL` for
compatibility with old setups.
```

Field respect user's adjustments in {attr}`wtf_field_class` option of
{class}`.db_fields.URLField`. This will change form field display, but will not
change inserted validators.

#### Examples

strings_demo.py in example app contain basic non-requirement example. You can adjust
it to any provided example for test purposes.

##### Not required URLField

```python
"""strings_demo.py"""
from example_app.models import db


class StringsDemoModel(db.Document):
    """Documentation example model."""

    url_field = db.URLField()
````

##### Required URLField with minimum size

```python
"""strings_demo.py"""
from example_app.models import db


class StringsDemoModel(db.Document):
    """Documentation example model."""

    required_url_field = db.URLField(required=True, min_length=25)
````

##### URLField with https only regexp check, if data exist

Regexp for {attr}`url_regex` should be prepared by {mod}`re`.

```python
"""strings_demo.py"""
import re

from example_app.models import db


class StringsDemoModel(db.Document):
    """Documentation example model."""

    https_url_field = db.URLField(
        url_regex=re.compile(
            r"^(https:\/\/)[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+,;=]+$"
        ),
    )
````

## Unsupported fields

### CachedReferenceField

Not yet documented. Please help us with new pull request.

### ComplexDateTimeField

Not yet documented. Please help us with new pull request.

### DynamicField

Not yet documented. Please help us with new pull request.

### EmbeddedDocumentListField

Not yet documented. Please help us with new pull request.

### EnumField

Not yet documented. Please help us with new pull request.

### GenericEmbeddedDocumentField

Not yet documented. Please help us with new pull request.

### GenericLazyReferenceField

Not yet documented. Please help us with new pull request.

### GeoJsonBaseField

Not yet documented. Please help us with new pull request.

### GeoPointField

Not yet documented. Please help us with new pull request.

### ImageField

Not yet documented. Please help us with new pull request.

### LazyReferenceField

Not yet documented. Please help us with new pull request.

### LineStringField

Not yet documented. Please help us with new pull request.

### LongField

Not yet documented. Please help us with new pull request.

### MapField

Not yet documented. Please help us with new pull request.

### MultiLineStringField

Not yet documented. Please help us with new pull request.

### MultiPointField

Not yet documented. Please help us with new pull request.

### MultiPolygonField

Not yet documented. Please help us with new pull request.

### PointField

Not yet documented. Please help us with new pull request.

### PolygonField

Not yet documented. Please help us with new pull request.

### SequenceField

Not yet documented. Please help us with new pull request.

### UUIDField

Not yet documented. Please help us with new pull request.

## Unsure

### GenericReferenceField

Not yet documented. Please help us with new pull request.

### ObjectIdField

Not yet documented. Please help us with new pull request.

[mongoengine]: https://docs.mongoengine.org/

[supported fields]: #supported-fields

[#379]: https://github.com/MongoEngine/flask-mongoengine/issues/379

[integration]: forms

[global transforms]: #global-transforms

[stringfield]: #stringfield

[wtforms]: https://wtforms.readthedocs.io/en/3.0.x/
